# crypto_agent.py

import os
import requests
import google.generativeai as genai
import logging
import re
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load API keys
gemini_api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
binance_api_key = st.secrets["BINANCE_API_KEY"] if "BINANCE_API_KEY" in st.secrets else os.getenv("BINANCE_API_KEY")
binance_api_secret = st.secrets["BINANCE_API_SECRET"] if "BINANCE_API_SECRET" in st.secrets else os.getenv("BINANCE_API_SECRET")

if not gemini_api_key:
    logger.error("GEMINI_API_KEY is not set.")
    raise ValueError("GEMINI_API_KEY is not set.")

# Configure Gemini
try:
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    raise

class CryptoDataAgent:
    def __init__(self, gemini_api_key, binance_api_key=None, binance_api_secret=None):
        self.google_model = genai.GenerativeModel('gemini-1.5-flash')
        self.binance_api_key = binance_api_key
        self.binance_api_secret = binance_api_secret
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.valid_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']

    def is_valid_symbol(self, symbol):
        return isinstance(symbol, str) and re.match(r'^[A-Z]{2,6}USDT$', symbol) and symbol in self.valid_symbols

    def get_crypto_price(self, symbol):
        if not self.is_valid_symbol(symbol):
            logger.error(f"Invalid symbol: {symbol}")
            return f"Error: Invalid symbol format: {symbol}"

        try:
            url = f"{self.binance_base_url}/ticker/price"
            response = requests.get(url, params={"symbol": symbol.upper()}, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("price", "N/A")
        except requests.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return f"Error: HTTP error for {symbol}: {str(e)}"
        except Exception as e:
            logger.error(f"Request error: {e}")
            return f"Error fetching price for {symbol}: {str(e)}"

    def interpret_query(self, query):
        try:
            prompt = (
                "You are an expert in cryptocurrency trading pairs. From the query: '{query}', "
                "extract the cryptocurrency trading pair (e.g., BTCUSDT for Bitcoin, ETHUSDT for Ethereum). "
                "Return only the trading pair in uppercase (e.g., BTCUSDT). If no valid pair is found, "
                "use this mapping: Bitcoin -> BTCUSDT, Ethereum -> ETHUSDT, Binance Coin -> BNBUSDT, "
                "Ripple -> XRPUSDT, Cardano -> ADAUSDT. If still unclear, return None."
            ).format(query=query)

            response = self.google_model.generate_content(prompt)
            symbol = response.text.strip()

            symbol_map = {
                "Bitcoin": "BTCUSDT",
                "Ethereum": "ETHUSDT",
                "Binance Coin": "BNBUSDT",
                "Ripple": "XRPUSDT",
                "Cardano": "ADAUSDT"
            }
            symbol = symbol_map.get(symbol, symbol)

            return symbol if self.is_valid_symbol(symbol) else None
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None

    def run(self, user_query):
        try:
            symbol = self.interpret_query(user_query)
            if symbol:
                price = self.get_crypto_price(symbol)
                return f"The current price of {symbol} is {price}"
            else:
                return "I couldn’t determine the cryptocurrency you’re asking about."
        except Exception as e:
            logger.error(f"Run error: {e}")
            return f"Unexpected error: {str(e)}"
