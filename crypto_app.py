import streamlit as st
from crypto_agent import CryptoDataAgent  # Make sure this file exists in the same repo

# Load secrets (from Streamlit Cloud settings)
gemini_api_key = st.secrets["GEMINI_API_KEY"]
binance_api_key = st.secrets["BINANCE_API_KEY"]
binance_api_secret = st.secrets["BINANCE_API_SECRET"]

# Initialize the agent
try:
    agent = CryptoDataAgent(gemini_api_key, binance_api_key, binance_api_secret)
except Exception as e:
    st.error(f"❌ Failed to initialize Crypto Agent: {e}")
    st.stop()

# Page config
st.set_page_config(page_title="HG Crypto Assistant", page_icon="💰")

# UI
st.title("💰 Crypto Price Assistant")
st.write("Ask about the price of Bitcoin, Ethereum, BNB, XRP, Cardano etc.")

query = st.text_input("🔍 Enter your query:", placeholder="e.g. What's the price of Ethereum?")

if st.button("Get Price"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Fetching price..."):
            try:
                result = agent.run(query)
                st.success("✅ Result:")
                st.write(result)
            except Exception as err:
                st.error(f"❌ Error while fetching price: {err}")

# Footer
st.markdown("""
<hr style="border-top: 1px solid #bbb;">
<div style='text-align: center; color: gray; font-size: small;'>
    Developed by Hadiqa Gohar 💻 | Powered by Gemini & Binance APIs 🔗
</div>
""", unsafe_allow_html=True)
