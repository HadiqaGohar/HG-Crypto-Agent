# crypto_app.py

import streamlit as st
# from agent import CryptoDataAgent  # Assuming your main class is saved in crypto_agent.py
from agent import CryptoDataAgent

import os
from dotenv import load_dotenv

# Load environment variables
if not load_dotenv():
    st.error(".env file not found or could not be loaded.")
    st.stop()


# Get API keys
gemini_api_key = os.getenv("GEMINI_API_KEY")
binance_api_key = os.getenv("BINANCE_API_KEY")
binance_api_secret = os.getenv("BINANCE_API_SECRET")

# Initialize the agent
try:
    agent = CryptoDataAgent(gemini_api_key, binance_api_key, binance_api_secret)
except Exception as e:
    st.error(f"Failed to initialize agent: {e}")
    st.stop()


# Set page config
st.set_page_config(page_title="HG Crypto Assistant", page_icon="💰")


# Streamlit UI
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
