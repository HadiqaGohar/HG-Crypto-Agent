# crypto_agent.py

import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import re



# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
if not load_dotenv():
    logger.error(".env file not found or could not be loaded.")
    print("Error: .env file not found or could not be loaded.")
    exit(1)

# Get API keys from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
binance_api_key = os.getenv("BINANCE_API_KEY")
binance_api_secret = os.getenv("BINANCE_API_SECRET")

# Check if Gemini API key is set
if not gemini_api_key:
    logger.error("GEMINI_API_KEY environment variable not set.")
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

# Configure Gemini API
try:
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    print(f"Error: Failed to configure Gemini API: {e}")
    exit(1)

class CryptoDataAgent:
    def __init__(self, gemini_api_key, binance_api_key=None, binance_api_secret=None):
        """Initialize the agent with Gemini and Binance API keys."""
        self.google_model = genai.GenerativeModel('gemini-1.5-flash')
        self.binance_api_key = binance_api_key
        self.binance_api_secret = binance_api_secret
        self.binance_base_url = "https://api.binance.com/api/v3"
        # Common trading pairs for validation
        self.valid_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']

    def is_valid_symbol(self, symbol):
        """Validate the cryptocurrency symbol format and existence."""
        if not isinstance(symbol, str):
            return False
        # Basic regex for Binance trading pair (e.g., BTCUSDT)
        if not re.match(r'^[A-Z]{2,6}USDT$', symbol):
            return False
        # Optionally, check against valid symbols (could query Binance API for full list)
        return symbol in self.valid_symbols

    def get_crypto_price(self, symbol):
        """Fetch the current price of a cryptocurrency using Binance API with requests."""
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
                logger.info(f"Successfully fetched price for {symbol}: {data['price']}")
                return data["price"]
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
                "extract the cryptocurrency trading pair (e.g., BTCUSDT for Bitcoin, ETHUSDT for Ethereum). "
                "Return only the trading pair in uppercase (e.g., BTCUSDT). If no valid pair is found, "
                "use this mapping: Bitcoin -> BTCUSDT, Ethereum -> ETHUSDT, Binance Coin -> BNBUSDT, "
                "Ripple -> XRPUSDT, Cardano -> ADAUSDT. If still unclear, return None."
            ).format(query=query)
            response = self.google_model.generate_content(prompt)
            symbol = response.text.strip()
            
            # Apply mapping for common names
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
            print(f"Error in Gemini API call: {e}")
            return None

    def run(self, user_query):
        """Execute the agent's workflow: interpret the query and fetch the price."""
        try:
            symbol = self.interpret_query(user_query)
            if symbol:
                price = self.get_crypto_price(symbol)
                return f"The current price of {symbol} is {price}"
            else:
                logger.warning(f"No valid cryptocurrency symbol found in query: {user_query}")
                return "I couldn’t determine the cryptocurrency you’re asking about."
        except Exception as e:
            logger.error(f"Unexpected error in run: {e}")
            return f"Error: Unexpected issue occurred: {str(e)}"

# Instantiate and execute the agent
try:
    agent = CryptoDataAgent(gemini_api_key, binance_api_key, binance_api_secret)
    response = agent.run("What’s the price of Bitcoin?")
    print(response)
except Exception as e:
    logger.error(f"Failed to initialize or run agent: {e}")
    print(f"Error: Failed to initialize or run agent: {str(e)}")
