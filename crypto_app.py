# crypto_app.py

import streamlit as st
from crypto_agent import CryptoDataAgent

# Set page config
st.set_page_config(page_title="HG Crypto Assistant", page_icon="💰")

# Get secrets
gemini_api_key = st.secrets["GEMINI_API_KEY"]
binance_api_key = st.secrets["BINANCE_API_KEY"]
binance_api_secret = st.secrets["BINANCE_API_SECRET"]

# Initialize agent
try:
    agent = CryptoDataAgent(gemini_api_key, binance_api_key, binance_api_secret)
except Exception as e:
    st.error(f"Failed to initialize CryptoDataAgent: {e}")
    st.stop()

# UI
st.title("💰 Crypto Price Assistant")
st.write("Ask about the price of Bitcoin, Ethereum, BNB, XRP, Cardano, etc.")

query = st.text_input("🔍 Enter your query:", placeholder="e.g. What's the price of Ethereum?")

# if st.button("Get Price"):
#     if not query.strip():
#         st.warning("Please enter a query.")
#     else:
#         with st.spinner("Fetching price..."):
#             result = agent.run(query)
#         st.success("Result:")
#         st.write(result)

if st.button("Get Price"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Fetching price..."):
            result = agent.run(query)
        if result:
            st.success("Result:")
            st.write(result)
        else:
            st.error("Something went wrong while fetching the price.")


# Footer
st.markdown("""
<hr style="border-top: 1px solid #bbb;">
<div style='text-align: center; color: gray; font-size: small;'>
    Developed by Hadiqa Gohar 💻 | Powered by Gemini & Binance APIs 🔗
</div>
""", unsafe_allow_html=True)
