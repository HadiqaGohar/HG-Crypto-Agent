# crypto_agent.py

import streamlit as st
import requests
import google.generativeai as genai
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get API keys from Streamlit secrets
gemini_api_key = st.secrets["GEMINI_API_KEY"]
binance_api_key = st.secrets["BINANCE_API_KEY"]
binance_api_secret = st.secrets["BINANCE_API_SECRET"]

# Configure Gemini API
try:
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    raise RuntimeError(f"Failed to configure Gemini API: {e}")

class CryptoDataAgent:
    def __init__(self, gemini_api_key, binance_api_key=None, binance_api_secret=None):
        self.google_model = genai.GenerativeModel('gemini-1.5-flash')
        self.binance_api_key = binance_api_key
        self.binance_api_secret = binance_api_secret
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.valid_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']

    def is_valid_symbol(self, symbol):
        if not isinstance(symbol, str):
            return False
        if not re.match(r'^[A-Z]{2,6}USDT$', symbol):
            return False
        return symbol in self.valid_symbols

    def get_crypto_price(self, symbol):
        if not self.is_valid_symbol(symbol):
            logger.error(f"Invalid symbol format: {symbol}")
            return f"Error: Invalid symbol format: {symbol}"
        
        try:
            url = f"{self.binance_base_url}/ticker/price"
            params = {"symbol": symbol.upper()}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "price" in data:
                logger.info(f"Price for {symbol}: {data['price']}")
                return data["price"]
            else:
                return f"Error: Invalid symbol {symbol}"
        except requests.Timeout:
            return f"Error: Request timeout for {symbol}"
        except requests.RequestException as e:
            return f"Error fetching price for {symbol}: {str(e)}"

    def interpret_query(self, query):
        try:
            prompt = (
                "You are an expert in cryptocurrency trading pairs. From the query: '{query}', "
                "extract the cryptocurrency trading pair (e.g., BTCUSDT for Bitcoin). "
                "If unknown, map common names like: Bitcoin -> BTCUSDT, Ethereum -> ETHUSDT, etc. "
                "Return only the trading pair or None if not found."
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

            if self.is_valid_symbol(symbol):
                return symbol
            return None
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
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
            return f"Error: Unexpected issue occurred: {str(e)}"
