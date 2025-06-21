import streamlit as st
from crypto_agent import CryptoDataAgent
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler (only if not in Streamlit Cloud)
if not os.getenv("STREAMLIT_SERVER_HEADLESS"):
    try:
        file_handler = logging.FileHandler('crypto_agent.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")

# Load API keys from Streamlit secrets or environment variables
try:
    gemini_api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    binance_api_key = st.secrets.get("BINANCE_API_KEY", os.getenv("BINANCE_API_KEY"))
    binance_api_secret = st.secrets.get("BINANCE_API_SECRET", os.getenv("BINANCE_API_SECRET"))
except Exception as e:
    logger.error(f"Error accessing secrets or environment variables: {e}")
    st.error(f"❌ Error accessing API keys: {e}")
    st.stop()

# Validate Gemini API key
if not gemini_api_key:
    logger.error("GEMINI_API_KEY not set in secrets or environment variables.")
    st.error("❌ GEMINI_API_KEY not set. Please set it in environment variables or Streamlit secrets.")
    st.stop()

# Initialize the agent
try:
    agent = CryptoDataAgent(gemini_api_key, binance_api_key, binance_api_secret)
except Exception as e:
    logger.error(f"Failed to initialize Crypto Agent: {e}")
    st.error(f"❌ Failed to initialize Crypto Agent: {e}")
    st.stop()

# Page config
st.set_page_config(page_title="HG Crypto Assistant", page_icon="💰")

# UI
st.title("💰 Crypto Price Assistant")
st.write("Ask about the price of Bitcoin, Ethereum, BNB, XRP, Cardano, etc.")

# Initialize session state for query and result
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'result' not in st.session_state:
    st.session_state.result = ""

# Input field and button
query = st.text_input("🔍 Enter your query:", placeholder="e.g. What's the price of Ethereum?", value=st.session_state.query)
if st.button("Get Price"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Fetching price..."):
            try:
                result = agent.run(query)
                st.session_state.result = result
                st.success("✅ Result:")
                st.write(result)
            except Exception as err:
                logger.error(f"Error while fetching price: {err}")
                st.session_state.result = f"❌ Error while fetching price: {err}"
                st.error(st.session_state.result)

# Display result
if st.session_state.result:
    st.write(st.session_state.result)

# Footer
st.markdown("""
<hr style="border-top: 1px solid #bbb;">
<div style='text-align: center; color: gray; font-size: small;'>
    Developed by Hadiqa Gohar 💻 | Powered by Gemini & Binance APIs 🔗
</div>
""", unsafe_allow_html=True)
