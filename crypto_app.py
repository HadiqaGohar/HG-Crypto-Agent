# # # # crypto_app.py

# # # import streamlit as st
# # # from agent import CryptoDataAgent  # Assuming your main class is saved in crypto_agent.py
# # # import os
# # # from dotenv import load_dotenv

# # # # Load environment variables
# # # if not load_dotenv():
# # #     st.error(".env file not found or could not be loaded.")
# # #     st.stop()


# # # # Get API keys
# # # gemini_api_key = os.getenv("GEMINI_API_KEY")
# # # binance_api_key = os.getenv("BINANCE_API_KEY")
# # # binance_api_secret = os.getenv("BINANCE_API_SECRET")

# # # # Initialize the agent
# # # try:
# # #     agent = CryptoDataAgent(gemini_api_key, binance_api_key, binance_api_secret)
# # # except Exception as e:
# # #     st.error(f"Failed to initialize agent: {e}")
# # #     st.stop()


# # # # Set page config
# # # st.set_page_config(page_title="HG Crypto Assistant", page_icon="💰")


# # # # Streamlit UI
# # # st.title("💰 Crypto Price Assistant")
# # # st.write("Ask about the price of Bitcoin, Ethereum, BNB, XRP, Cardano etc.")

# # # query = st.text_input("🔍 Enter your query:", placeholder="e.g. What's the price of Ethereum?")

# # # if st.button("Get Price"):
# # #     if not query.strip():
# # #         st.warning("Please enter a query.")
# # #     else:
# # #         with st.spinner("Fetching price..."):
# # #             result = agent.run(query)
# # #         st.success("Result:")
# # #         st.write(result)
# # # # Footer
# # # st.markdown("""
# # # <hr style="border-top: 1px solid #bbb;">
# # # <div style='text-align: center; color: gray; font-size: small;'>
# # #     Developed by HadiqaGohar 💻 | Powered by Gemini & Binance APIs 🔗
# # # </div>
# # # """, unsafe_allow_html=True)



# # import streamlit as st
# # import os
# # from dotenv import load_dotenv
# # from agent import CryptoDataAgent

# # # Load environment variables for local development (optional)
# # load_dotenv()  # No error if .env is missing, as Streamlit Cloud uses secrets

# # # Get API keys from environment variables or Streamlit secrets
# # try:
# #     BINANCE_API_KEY = os.getenv("BINANCE_API_KEY") or st.secrets["BINANCE_API_KEY"]
# #     BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET") or st.secrets["BINANCE_API_SECRET"]
# #     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]
# # except KeyError as e:
# #     st.error(f"Missing API key: {e}. Please configure it in Streamlit Cloud secrets or local .env.")
# #     st.stop()

# # # Initialize the agent
# # try:
# #     agent = CryptoDataAgent(GEMINI_API_KEY, BINANCE_API_KEY, BINANCE_API_SECRET)
# # except Exception as e:
# #     st.error(f"Failed to initialize agent: {e}")
# #     st.stop()

# # # Set page config
# # st.set_page_config(page_title="HG Crypto Assistant", page_icon="💰")

# # # Streamlit UI
# # st.title("💰 Crypto Price Assistant")
# # st.write("Ask about the price of Bitcoin, Ethereum, BNB, XRP, Cardano, etc.")

# # query = st.text_input("🔍 Enter your query:", placeholder="e.g. What's the price of Ethereum?")

# # if st.button("Get Price"):
# #     if not query.strip():
# #         st.warning("Please enter a query.")
# #     else:
# #         with st.spinner("Fetching price..."):
# #             result = agent.run(query)
# #         st.success("Result:")
# #         st.write(result)

# # # Footer
# # st.markdown("""
# # <hr style="border-top: 1px solid #bbb;">
# # <div style='text-align: center; color: gray; font-size: small;'>
# #     Developed by HadiqaGohar 💻 | Powered by Gemini & Binance APIs 🔗
# # </div>
# # """, unsafe_allow_html=True)









# import streamlit as st
# import os
# from dotenv import load_dotenv
# from agent import CryptoDataAgent

# # Load environment variables for local development (optional, no error if missing)
# load_dotenv()  # Silent failure if .env is not found

# # Get API keys from environment variables or Streamlit secrets
# try:
#     BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
#     BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
#     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

#     # Fall back to Streamlit secrets if environment variables are not set
#     if not all([BINANCE_API_KEY, BINANCE_API_SECRET, GEMINI_API_KEY]):
#         BINANCE_API_KEY = BINANCE_API_KEY or st.secrets.get("BINANCE_API_KEY")
#         BINANCE_API_SECRET = BINANCE_API_SECRET or st.secrets.get("BINANCE_API_SECRET")
#         GEMINI_API_KEY = GEMINI_API_KEY or st.secrets.get("GEMINI_API_KEY")

#     if not all([BINANCE_API_KEY, BINANCE_API_SECRET, GEMINI_API_KEY]):
#         raise KeyError("One or more API keys are missing")
# except KeyError as e:
#     st.error(f"Missing API key: {e}. Please configure it in Streamlit Cloud secrets or local .env.")
#     st.stop()

# # Initialize the agent
# try:
#     agent = CryptoDataAgent(GEMINI_API_KEY, BINANCE_API_KEY, BINANCE_API_SECRET)
# except Exception as e:
#     st.error(f"Failed to initialize agent: {e}")
#     st.stop()

# # Set page config
# st.set_page_config(page_title="HG Crypto Assistant", page_icon="💰")

# # Streamlit UI
# st.title("💰 Crypto Price Assistant")
# st.write("Ask about the price of Bitcoin, Ethereum, BNB, XRP, Cardano, etc.")

# query = st.text_input("🔍 Enter your query:", placeholder="e.g. What's the price of Ethereum?")

# if st.button("Get Price"):
#     if not query.strip():
#         st.warning("Please enter a query.")
#     else:
#         with st.spinner("Fetching price..."):
#             result = agent.run(query)
#         st.success("Result:")
#         st.write(result)

# # Footer
# st.markdown("""
# <hr style="border-top: 1px solid #bbb;">
# <div style='text-align: center; color: gray; font-size: small;'>
#     Developed by HadiqaGohar 💻 | Powered by Gemini & Binance APIs 🔗
# </div>
# """, unsafe_allow_html=True)











import streamlit as st
import os
from dotenv import load_dotenv
from agent import CryptoDataAgent

# Load environment variables for local development (optional, no error if missing)
load_dotenv()  # Silent failure if .env is not found

# Get API keys from environment variables or Streamlit secrets
try:
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Fall back to Streamlit secrets if environment variables are not set
    if not all([BINANCE_API_KEY, BINANCE_API_SECRET, GEMINI_API_KEY]):
        BINANCE_API_KEY = BINANCE_API_KEY or st.secrets.get("BINANCE_API_KEY")
        BINANCE_API_SECRET = BINANCE_API_SECRET or st.secrets.get("BINANCE_API_SECRET")
        GEMINI_API_KEY = GEMINI_API_KEY or st.secrets.get("GEMINI_API_KEY")

    if not all([BINANCE_API_KEY, BINANCE_API_SECRET, GEMINI_API_KEY]):
        raise KeyError("One or more API keys are missing")
except KeyError as e:
    st.error(f"Missing API key: {e}. Please configure it in Streamlit Cloud secrets or local .env.")
    st.stop()

# Initialize the agent
try:
    agent = CryptoDataAgent(GEMINI_API_KEY, BINANCE_API_KEY, BINANCE_API_SECRET)
except Exception as e:
    st.error(f"Failed to initialize agent: {e}")
    st.stop()

# Set page config
st.set_page_config(page_title="HG Crypto Assistant", page_icon="💰")

# Streamlit UI
st.title("💰 Crypto Price Assistant")
st.write("Ask about the price of Bitcoin, Ethereum, BNB, XRP, Cardano, etc.")

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
