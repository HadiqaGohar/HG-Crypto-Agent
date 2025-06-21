# agent.py

import os
import requests
import google.generativeai as genai
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- API Keys are now passed in through the constructor from crypto_app.py ---
# This file (agent.py) should not directly load environment variables or secrets.

class CryptoDataAgent:
    def __init__(self, gemini_api_key, binance_api_key=None, binance_api_secret=None):
        """Initialize the agent with Gemini and Binance API keys."""
        # Validate API keys before proceeding
        if not gemini_api_key:
            logger.error("Gemini API Key is missing.")
            raise ValueError("Gemini API Key is required.")

        try:
            genai.configure(api_key=gemini_api_key)
            self.google_model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise RuntimeError(f"Failed to configure Gemini API: {e}")

        self.binance_api_key = binance_api_key
        self.binance_api_secret = binance_api_secret
        self.binance_base_url = "https://api.binance.com/api/v3"
        
        # Common trading pairs for validation
        self.valid_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']
        logger.info("CryptoDataAgent initialized successfully.")

    def is_valid_symbol(self, symbol):
        """Validate the cryptocurrency symbol format and existence."""
        if not isinstance(symbol, str):
            logger.debug(f"Invalid symbol type: {type(symbol)}")
            return False
        
        # Basic regex for Binance trading pair (e.g., BTCUSDT)
        # Allows 2 to 6 uppercase letters followed by USDT
        if not re.match(r'^[A-Z]{2,6}USDT$', symbol):
            logger.debug(f"Symbol '{symbol}' does not match regex pattern.")
            return False
        
        # Optionally, check against a predefined list for common symbols
        # For a full production app, you might query Binance for a real-time list,
        # but for this context, the hardcoded list is sufficient.
        if symbol not in self.valid_symbols:
            logger.warning(f"Symbol '{symbol}' not in pre-defined valid symbols. Attempting to proceed.")
            # For robustness, we will still allow unlisted symbols to be queried,
            # as Binance API will return an error if it's truly invalid.
        return True

    def get_crypto_price(self, symbol):
        """Fetch the current price of a cryptocurrency using Binance API with requests."""
        symbol = symbol.upper() # Ensure symbol is uppercase
        if not self.is_valid_symbol(symbol):
            logger.error(f"Invalid symbol format received for price fetch: {symbol}")
            return f"Error: Invalid cryptocurrency symbol '{symbol}'. Please use a valid trading pair like BTCUSDT."
        
        try:
            url = f"{self.binance_base_url}/ticker/price"
            params = {"symbol": symbol}
            logger.info(f"Fetching price for {symbol} from {url}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if "price" in data:
                logger.info(f"Successfully fetched price for {symbol}: {data['price']}")
                return float(data["price"]) # Return as float for numerical operations
            elif "msg" in data: # Binance API often returns 'msg' on error
                logger.error(f"Binance API error for {symbol}: {data['msg']}")
                return f"Error from Binance: {data['msg']} (Symbol: {symbol})"
            else:
                logger.error(f"Unexpected response from Binance for {symbol}: {data}")
                return f"Error: Could not retrieve price for {symbol}. Unexpected response."
        except requests.Timeout:
            logger.error(f"Request timeout when fetching price for {symbol}.")
            return f"Error: Request timed out while fetching price for {symbol}."
        except requests.HTTPError as e:
            logger.error(f"HTTP error for {symbol}: {e.response.status_code} - {e.response.text}")
            return f"Error: HTTP {e.response.status_code} for {symbol}. Details: {e.response.text}"
        except requests.ConnectionError:
            logger.error(f"Connection error when fetching price for {symbol}.")
            return f"Error: Could not connect to Binance API for {symbol}. Check your internet connection."
        except requests.RequestException as e:
            logger.error(f"General request error for {symbol}: {e}")
            return f"Error fetching price for {symbol}: {str(e)}"
        except ValueError as e:
            logger.error(f"Error parsing price for {symbol}: {e}")
            return f"Error: Price data for {symbol} is not valid."

    def interpret_query(self, query):
        """Use Gemini to interpret the query and extract the cryptocurrency symbol."""
        try:
            prompt = (
                "You are an expert in cryptocurrency trading pairs. From the query: '{query}', "
                "extract the primary cryptocurrency trading pair (e.g., BTCUSDT for Bitcoin, ETHUSDT for Ethereum). "
                "Return ONLY the trading pair in uppercase (e.g., BTCUSDT). "
                "If the query explicitly mentions a common cryptocurrency name but not a direct symbol, "
                "use this mapping: Bitcoin -> BTCUSDT, Ethereum -> ETHUSDT, Binance Coin -> BNBUSDT, "
                "Ripple -> XRPUSDT, Cardano -> ADAUSDT. "
                "If no clear, valid trading pair or common name mapping is found, return the exact string 'NONE_FOUND'."
                "\nExamples:\n"
                "Query: 'What is the current price of Bitcoin?' -> Response: 'BTCUSDT'\n"
                "Query: 'Price of ETH?' -> Response: 'ETHUSDT'\n"
                "Query: 'How much is Cardano?' -> Response: 'ADAUSDT'\n"
                "Query: 'Current value of Dogecoin?' -> Response: 'DOGEUSDT'\n" # Example for a coin not in explicit mapping
                "Query: 'What's the weather like?' -> Response: 'NONE_FOUND'\n"
            ).format(query=query)
            
            logger.info(f"Sending prompt to Gemini: {prompt[:100]}...") # Log first 100 chars
            response = self.google_model.generate_content(prompt)
            symbol = response.text.strip().upper() # Ensure the symbol is uppercase

            if symbol == 'NONE_FOUND':
                logger.warning(f"Gemini could not identify a symbol for query: '{query}'")
                return None

            # Validate the extracted symbol against our format
            if self.is_valid_symbol(symbol):
                logger.info(f"Extracted valid symbol: {symbol} for query: '{query}'")
                return symbol
            else:
                logger.warning(f"Gemini extracted an invalid format symbol: '{symbol}' for query: '{query}'")
                return None
        except Exception as e:
            logger.error(f"Gemini API error during query interpretation for '{query}': {e}", exc_info=True)
            return None

    def run(self, user_query):
        """Execute the agent's workflow: interpret the query and fetch the price."""
        if not user_query or not user_query.strip():
            return "Please provide a query to get crypto prices."

        try:
            symbol = self.interpret_query(user_query)
            if symbol:
                price_result = self.get_crypto_price(symbol)
                # Check if price_result is an error message
                if isinstance(price_result, str) and price_result.startswith("Error:"):
                    return f"Failed to get price for {symbol}: {price_result}"
                else:
                    return f"The current price of {symbol} is ${price_result:,.4f}" # Format price to 4 decimal places
            else:
                logger.warning(f"No valid cryptocurrency symbol found for query: '{user_query}'")
                return "I couldn’t determine the cryptocurrency you’re asking about. Please be more specific (e.g., 'Bitcoin', 'ETHUSDT')."
        except Exception as e:
            logger.error(f"Unexpected error in agent.run for query '{user_query}': {e}", exc_info=True)
            return f"An unexpected issue occurred: {str(e)}. Please try again."

