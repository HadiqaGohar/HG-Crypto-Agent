# crypto_app.py

import streamlit as st
from agent import CryptoDataAgent  # Import the agent from the 'agent.py' file
import os

# --- Configuration for Streamlit Secrets ---
# In your Streamlit Cloud app settings, you need to add your secrets:
# File name: .streamlit/secrets.toml
#
# [secrets]
# GEMINI_API_KEY = "your_gemini_api_key_here"
# BINANCE_API_KEY = "your_binance_api_key_here"
# BINANCE_API_SECRET = "your_binance_api_secret_here"
#
# Replace "your_..." with your actual keys.

# Get API keys from Streamlit secrets
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    # Binance keys are optional for fetching public data like price, but good to include if present
    binance_api_key = st.secrets.get("BINANCE_API_KEY")
    binance_api_secret = st.secrets.get("BINANCE_API_SECRET")
except KeyError as e:
    st.error(f"Missing Streamlit secret: {e}. Please ensure GEMINI_API_KEY is set in your Streamlit secrets.")
    st.info("To set secrets, go to your app settings on Streamlit Cloud -> 'Secrets' and add them.")
    st.stop() # Stop the app if essential secrets are missing

# Initialize the agent
# Use st.session_state to ensure the agent is only initialized once
if 'agent' not in st.session_state:
    try:
        st.session_state.agent = CryptoDataAgent(
            gemini_api_key=gemini_api_key,
            binance_api_key=binance_api_key,
            binance_api_secret=binance_api_secret
        )
    except (ValueError, RuntimeError) as e:
        st.error(f"Failed to initialize Crypto Agent: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred during agent initialization: {e}")
        st.stop()

# Streamlit UI
st.set_page_config(page_title="HG Crypto Assistant", page_icon="💰", layout="centered")

st.title("💰 Crypto Price Assistant")
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #ddd;
        padding: 10px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }
    h1 {
        text-align: center;
        color: #FFD700; /* Gold */
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .stSuccess {
        background-color: #e6ffe6;
        color: #006600;
        border-left: 5px solid #4CAF50;
        padding: 10px;
        border-radius: 5px;
    }
    .stWarning {
        background-color: #fffacd;
        color: #8a6d3b;
        border-left: 5px solid #f0ad4e;
        padding: 10px;
        border-radius: 5px;
    }
    .footer {
        font-size: small;
        color: gray;
        text-align: center;
        margin-top: 20px;
        padding-top: 10px;
        border-top: 1px solid #bbb;
    }
</style>
""", unsafe_allow_html=True)

st.write("Ask about the current price of cryptocurrencies like **Bitcoin**, **Ethereum**, **BNB**, **XRP**, **Cardano**, etc.")

query = st.text_input("🔍 Enter your query:", placeholder="e.g. What's the price of Ethereum?", key="user_query")

if st.button("Get Price", key="get_price_button"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Fetching price... This might take a moment as AI interprets the query and fetches data..."):
            # Access the agent from session_state
            result = st.session_state.agent.run(query)
        st.success("Result:")
        st.write(result)

# Footer
st.markdown("""
<div class="footer">
    Developed by HadiqaGohar 💻 | Powered by Gemini & Binance APIs 🔗
</div>
""", unsafe_allow_html=True)

