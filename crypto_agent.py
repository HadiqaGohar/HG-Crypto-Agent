<<<<<<< HEAD
# crypto_agent.py

import os
=======
>>>>>>> 99b800d20abce9f4af4913b4dbea793f067486af
import requests
import google.generativeai as genai
import logging
import re
import os

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler (only if not in Streamlit Cloud)
if not os.getenv("STREAMLIT_SERVER_HEADLESS"):  # Detect non-Cloud environment
    try:
        file_handler = logging.FileHandler('crypto_agent.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")

class CryptoDataAgent:
    def __init__(self, gemini_api_key, binance_api_key=None, binance_api_secret=None):
        """Initialize the agent with Gemini and Binance API keys."""
        try:
            genai.configure(api_key=gemini_api_key)
            self.google_model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise Exception(f"Failed to configure Gemini API: {e}")
        self.binance_api_key = binance_api_key
        self.binance_api_secret = binance_api_secret
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.valid_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']

    def is_valid_symbol(self, symbol):
        """Validate the cryptocurrency symbol format and existence."""
        if not isinstance(symbol, str):
            return False
        if not re.match(r'^[A-Z]{2,6}USDT$', symbol):
            return False
        return symbol in self.valid_symbols

    def get_crypto_price(self, symbol):
        """Fetch the current price of a cryptocurrency using Binance API."""
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
                price = float(data["price"])
                logger.info(f"Successfully fetched price for {symbol}: {price}")
                return f"{price:.2f}"  # Format to 2 decimal places
            else:
                logger.error(f"Invalid symbol response from Binance: {data}")
                return f"Error: Invalid symbol {symbol}"
        except requests.Timeout:
            logger.error(f"Request timeout for {symbol}")
            return f"Error: Request timeout for {symbol}"
        except requests.HTTPError as e:
            logger.error(f"HTTP error for {symbol}: {e}")
            return f"Error: HTTP error for {symbol}: {str(e)}"
        except requests.ConnectionError:
            logger.error(f"Connection error for {symbol}")
            return f"Error: Connection error for {symbol}"
        except requests.RequestException as e:
            logger.error(f"Request error for {symbol}: {e}")
            return f"Error fetching price for {symbol}: {str(e)}"

    def interpret_query(self, query):
        """Use Gemini to interpret the query and extract the cryptocurrency symbol."""
        try:
            prompt = (
                "You are an expert in cryptocurrency trading pairs. From the query: '{query}', "
                "extract the cryptocurrency trading pair (e.g., BTCUSDT for Bitcoin). "
                "Return only the trading pair in uppercase (e.g., BTCUSDT). "
                "Use this mapping if needed: Bitcoin -> BTCUSDT, Ethereum -> ETHUSDT, "
                "Binance Coin -> BNBUSDT, Ripple -> XRPUSDT, Cardano -> ADAUSDT. "
                "If no valid pair is found, return None."
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
                logger.info(f"Extracted valid symbol: {symbol}")
                return symbol
            logger.warning(f"Invalid or no symbol extracted: {symbol}")
            return None
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"Error in Gemini API call: {e}"

    def run(self, user_query):
        """Execute the agent's workflow: interpret the query and fetch the price."""
        try:
            symbol = self.interpret_query(user_query)
            if symbol:
                price = self.get_crypto_price(symbol)
                return f"The current price of {symbol} is {price} USDT"
            else:
                logger.warning(f"No valid cryptocurrency symbol found in query: {user_query}")
                return "I couldn’t determine the cryptocurrency you’re asking about."
        except Exception as e:
            logger.error(f"Unexpected error in run: {e}")
            return f"Error: Unexpected issue occurred: {str(e)}"
