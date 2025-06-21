import streamlit as st
import requests
import google.generativeai as genai
import logging
import re

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API keys from Streamlit secrets
gemini_api_key = st.secrets["GEMINI_API_KEY"]
binance_api_key = st.secrets["BINANCE_API_KEY"]import requests
import google.generativeai as genai
import logging
import re

# Logger config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoDataAgent:
    def __init__(self, gemini_api_key, binance_api_key=None, binance_api_secret=None):
        genai.configure(api_key=gemini_api_key)
        self.google_model = genai.GenerativeModel('gemini-1.5-flash')
        self.binance_api_key = binance_api_key
        self.binance_api_secret = binance_api_secret
        self.base_url = "https://api.binance.com/api/v3"
        self.valid_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']

    def is_valid_symbol(self, symbol):
        return isinstance(symbol, str) and re.match(r'^[A-Z]{2,6}USDT$', symbol) and symbol in self.valid_symbols

    def get_crypto_price(self, symbol):
        try:
            response = requests.get(f"{self.base_url}/ticker/price", params={"symbol": symbol}, timeout=10)
            response.raise_for_status()
            return response.json()["price"]
        except Exception as e:
            logger.error(f"Error fetching {symbol} price: {e}")
            return f"Error: {e}"

    def interpret_query(self, query):
        try:
            prompt = (
                f"You are a crypto expert. Extract the trading pair from the query: '{query}'. "
                f"Respond with only: BTCUSDT, ETHUSDT, BNBUSDT, XRPUSDT, ADAUSDT. If unclear, return NONE."
            )
            response = self.google_model.generate_content(prompt)
            symbol = response.text.strip().upper()
            fallback = {
                "BITCOIN": "BTCUSDT",
                "ETHEREUM": "ETHUSDT",
                "BNB": "BNBUSDT",
                "RIPPLE": "XRPUSDT",
                "CARDANO": "ADAUSDT",
                "NONE": None
            }
            symbol = fallback.get(symbol, symbol)
            return symbol if self.is_valid_symbol(symbol) else None
        except Exception as e:
            logger.error(f"Interpretation failed: {e}")
            return None

    def run(self, user_query):
        symbol = self.interpret_query(user_query)
        if symbol:
            price = self.get_crypto_price(symbol)
            return f"The current price of {symbol} is {price}"
        else:
            return "Sorry, I couldn't determine which crypto you meant."

binance_api_secret = st.secrets["BINANCE_API_SECRET"]

# Configure Gemini
genai.configure(api_key=gemini_api_key)

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
            return f"Error: Invalid symbol format: {symbol}"
        try:
            url = f"{self.binance_base_url}/ticker/price"
            response = requests.get(url, params={"symbol": symbol}, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("price", f"Error: Invalid symbol {symbol}")
        except requests.RequestException as e:
            return f"Error fetching price for {symbol}: {str(e)}"

    def interpret_query(self, query):
        prompt = (
            f"From this query: '{query}', extract the crypto pair like BTCUSDT or use Bitcoin -> BTCUSDT, Ethereum -> ETHUSDT, etc."
        )
        try:
            response = self.google_model.generate_content(prompt)
            symbol = response.text.strip().upper()
            symbol_map = {
                "BITCOIN": "BTCUSDT",
                "ETHEREUM": "ETHUSDT",
                "BINANCE COIN": "BNBUSDT",
                "RIPPLE": "XRPUSDT",
                "CARDANO": "ADAUSDT"
            }
            symbol = symbol_map.get(symbol, symbol)
            return symbol if self.is_valid_symbol(symbol) else None
        except Exception as e:
            return None

    def run(self, user_query):
        symbol = self.interpret_query(user_query)
        if symbol:
            price = self.get_crypto_price(symbol)
            return f"The current price of {symbol} is {price}"
        else:
            return "Sorry, I couldn't determine which crypto you meant."
