# crypto_app.py

import streamlit as st
from agent import CryptoDataAgent
import os

# Get API keys - works for both local and Streamlit Cloud
gemini_api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
binance_api_key = st.secrets["BINANCE_API_KEY"] if "BINANCE_API_KEY" in st.secrets else os.getenv("BINANCE_API_KEY")
binance_api_secret = st.secrets["BINANCE_API_SECRET"] if "BINANCE_API_SECRET" in st.secrets else os.getenv("BINANCE_API_SECRET")

# Validate keys
if not gemini_api_key or not binance_api_key:
    st.error("API keys are missing. Please check your Streamlit secrets or .env file.")
    st.stop()

# Initialize agent
try:
    agent = CryptoDataAgent(gemini_api_key, binance_api_key, binance_api_secret)
except Exception as e:
    st.error(f"Failed to initialize agent: {e}")
    st.stop()

# Streamlit UI
st.set_page_config(page_title="HG Crypto Assistant", page_icon="💰")
st.title("💰 Crypto Price Assistant")
st.write("Ask about the price of Bitcoin, Ethereum, BNB, XRP, Cardano etc.")

query = st.text_input("🔍 Enter your query:", placeholder="e.g. What's the price of Ethereum?")

if st.button("Get Price"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Fetching price..."):
            result = agent.run(query)
        st.success("Result:")
        st.write(result)

# Footer
st.markdown("""
<hr style="border-top: 1px solid #bbb;">
<div style='text-align: center; color: gray; font-size: small;'>
    Developed by HadiqaGohar 💻 | Powered by Gemini & Binance APIs 🔗
</div>
""", unsafe_allow_html=True)
