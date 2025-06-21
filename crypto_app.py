import streamlit as st
from crypto_agent import CryptoDataAgent

# Set up Streamlit UI
st.set_page_config(page_title="💰 HG Crypto Assistant", page_icon="💰")
st.title("💰 Crypto Price Assistant")
st.write("Ask about the price of Bitcoin, Ethereum, BNB, XRP, Cardano, etc.")

# Initialize the agent
try:
    agent = CryptoDataAgent(
        gemini_api_key=st.secrets["GEMINI_API_KEY"],
        binance_api_key=st.secrets["BINANCE_API_KEY"],
        binance_api_secret=st.secrets["BINANCE_API_SECRET"]
    )
except Exception as e:
    st.error(f"Agent initialization failed: {e}")
    st.stop()

# User input
query = st.text_input("🔍 Enter your query:", placeholder="e.g. What's the price of Bitcoin?")

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
    Developed by HadiqaGohar 💻 | Powered by Gemini & Binance APIs 🔗
</div>
""", unsafe_allow_html=True)
