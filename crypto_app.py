import streamlit as st
from crypto_agent import CryptoDataAgent

st.set_page_config(page_title="Crypto Price Agent", layout="centered")
st.title("💹 Crypto Price Agent")
st.markdown("Ask about the price of any cryptocurrency (e.g., 'What is the price of Bitcoin?').")

# Input
user_query = st.text_input("Enter your query:")

# Process & Display
if user_query:
    with st.spinner("Getting response..."):
        agent = CryptoDataAgent(
            st.secrets["GEMINI_API_KEY"],
            st.secrets["BINANCE_API_KEY"],
            st.secrets["BINANCE_API_SECRET"]
        )
        result = agent.run(user_query)
        st.success(result)
