# agent.py

import os
import requests
import google.generativeai as genai
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- IMPORTANT: API Keys are now PASSED IN through the constructor from crypto_app.py ---
# This file (agent.py) should NOT directly load environment variables or secrets using dotenv or os.getenv.

class CryptoDataAgent:
    def __init__(self, gemini_api_key, binance_api_key=None, binance_api_secret=None):
        """Initialize the agent with Gemini and Binance API keys.
        
        Args:
            gemini_api_key (str): The API key for Google Gemini.
            binance_api_key (str, optional): The API key for Binance. Defaults to None.
            binance_api_secret (str, optional): The API secret for Binance. Defaults to None.
        
        Raises:
            ValueError: If gemini_api_key is missing.
            RuntimeError: If Gemini API configuration fails.
        """
        # Validate essential API key before proceeding
        if not gemini_api_key:
            logger.error("Gemini API Key is missing. Cannot initialize CryptoDataAgent.")
            raise ValueError("Gemini API Key is required for the agent to function.")

        # Configure Gemini API
        try:
            genai.configure(api_key=gemini_api_key)
            self.google_model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini API configured successfully.")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}", exc_info=True)
            raise RuntimeError(f"Failed to configure Gemini API: {e}. Please check your API key and network connection.")

        self.binance_api_key = binance_api_key
        self.binance_api_secret = binance_api_secret
        self.binance_base_url = "https://api.binance.com/api/v3"
        
        # Predefined common trading pairs for initial validation and suggestions
        self.valid_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'SOLUSDT', 'DOTUSDT']
        logger.info("CryptoDataAgent initialized successfully with provided API keys.")

    def is_valid_symbol(self, symbol):
        """
        Validate the cryptocurrency symbol format.
        Checks for uppercase letters followed by 'USDT'.
        
        Args:
            symbol (str): The cryptocurrency symbol to validate (e.g., 'BTCUSDT').
            
        Returns:
            bool: True if the symbol format is valid, False otherwise.
        """
        if not isinstance(symbol, str):
            logger.debug(f"Invalid symbol type: {type(symbol)}. Expected string.")
            return False
        
        # Regex to match 2 to 6 uppercase letters (for the crypto part) followed by 'USDT'
        # Example: BTCUSDT, ETHUSDT, XRPUSDT, SOLUSDT
        if not re.match(r'^[A-Z]{2,6}USDT$', symbol):
            logger.debug(f"Symbol '{symbol}' does not match expected Binance trading pair format (e.g., BTCUSDT).")
            return False
        
        # While the regex checks the format, the Binance API itself will validate existence.
        # The self.valid_symbols list serves as a quick check for common coins.
        return True

    def get_crypto_price(self, symbol):
        """
        Fetch the current price of a cryptocurrency using the Binance API.
        
        Args:
            symbol (str): The cryptocurrency trading pair symbol (e.g., 'BTCUSDT').
            
        Returns:
            Union[float, str]: The current price as a float if successful, 
                               or an error message string if an error occurs.
        """
        symbol = symbol.upper() # Ensure the symbol is in uppercase for API consistency
        
        if not self.is_valid_symbol(symbol):
            logger.error(f"Attempted to fetch price for an invalid symbol format: '{symbol}'")
            return f"Error: The cryptocurrency symbol '{symbol}' is not in a recognized format (e.g., BTCUSDT)."
        
        try:
            url = f"{self.binance_base_url}/ticker/price"
            params = {"symbol": symbol}
            
            logger.info(f"Attempting to fetch price for {symbol} from Binance API.")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            
            data = response.json()

            if "price" in data:
                price = float(data["price"])
                logger.info(f"Successfully fetched price for {symbol}: {price}")
                return price
            elif "msg" in data: # Binance API often returns an 'msg' field with error details
                logger.error(f"Binance API returned an error for symbol '{symbol}': {data['msg']}")
                return f"Error from Binance: {data['msg']} (Symbol: {symbol})"
            else:
                logger.error(f"Unexpected response structure from Binance for {symbol}: {data}")
                return f"Error: Could not retrieve price for {symbol}. Unexpected API response."
        
        except requests.Timeout:
            logger.error(f"Request timed out while fetching price for {symbol}.")
            return f"Error: Request to Binance API timed out for {symbol}. Please try again later."
        except requests.HTTPError as e:
            logger.error(f"HTTP error occurred while fetching price for {symbol}: {e.response.status_code} - {e.response.text}", exc_info=True)
            return f"Error: Received HTTP {e.response.status_code} from Binance for {symbol}. Details: {e.response.text}"
        except requests.ConnectionError:
            logger.error(f"Network connection error while fetching price for {symbol}.")
            return f"Error: Could not connect to Binance API for {symbol}. Please check your internet connection."
        except requests.RequestException as e:
            logger.error(f"A general request error occurred for {symbol}: {e}", exc_info=True)
            return f"Error fetching price for {symbol}: {str(e)}"
        except ValueError as e:
            logger.error(f"Error parsing price data for {symbol}: {e}. Raw data: {data}", exc_info=True)
            return f"Error: Price data for {symbol} could not be parsed correctly."

    def interpret_query(self, query):
        """
        Uses the Gemini model to interpret a natural language query and extract a cryptocurrency symbol.
        
        Args:
            query (str): The user's natural language query (e.g., "What's the price of Bitcoin?").
            
        Returns:
            Union[str, None]: The extracted uppercase cryptocurrency symbol (e.g., 'BTCUSDT'), 
                              or None if no valid symbol can be determined.
        """
        try:
            prompt = (
                "You are an expert in cryptocurrency trading pairs. From the query: '{query}', "
                "extract the primary cryptocurrency trading pair (e.g., BTCUSDT for Bitcoin, ETHUSDT for Ethereum). "
                "Return ONLY the trading pair in uppercase (e.g., BTCUSDT). "
                "If the query explicitly mentions a common cryptocurrency name but not a direct symbol, "
                "use this mapping: Bitcoin -> BTCUSDT, Ethereum -> ETHUSDT, Binance Coin -> BNBUSDT, "
                "Ripple -> XRPUSDT, Cardano -> ADAUSDT, Dogecoin -> DOGEUSDT, Solana -> SOLUSDT, Polkadot -> DOTUSDT. "
                "If still unclear or if the query is unrelated to cryptocurrencies, return the exact string 'NONE_FOUND'."
                "\nExamples:\n"
                "Query: 'What is the current price of Bitcoin?' -> Response: 'BTCUSDT'\n"
                "Query: 'Price of ETH?' -> Response: 'ETHUSDT'\n"
                "Query: 'How much is Cardano?' -> Response: 'ADAUSDT'\n"
                "Query: 'Current value of Dogecoin?' -> Response: 'DOGEUSDT'\n"
                "Query: 'What's the weather like?' -> Response: 'NONE_FOUND'\n"
                "Query: 'Tell me about the stock market.' -> Response: 'NONE_FOUND'\n"
            ).format(query=query)
            
            logger.info(f"Sending prompt to Gemini for query interpretation: '{query}'")
            response = self.google_model.generate_content(prompt, safety_settings={'HARASSMENT': 'BLOCK_NONE', 'HATE_SPEECH': 'BLOCK_NONE', 'SEXUALLY_EXPLICIT': 'BLOCK_NONE', 'DANGEROUS_CONTENT': 'BLOCK_NONE'})
            
            # Check if response.text exists and is not empty
            if not response.text:
                logger.warning(f"Gemini returned an empty response for query: '{query}'")
                return None

            extracted_symbol = response.text.strip().upper() # Ensure the symbol is uppercase and remove whitespace

            if extracted_symbol == 'NONE_FOUND':
                logger.warning(f"Gemini could not identify a valid crypto symbol for query: '{query}'")
                return None
            
            # Final validation of the extracted symbol before returning
            if self.is_valid_symbol(extracted_symbol):
                logger.info(f"Successfully extracted and validated symbol '{extracted_symbol}' for query: '{query}'")
                return extracted_symbol
            else:
                logger.warning(f"Gemini extracted symbol '{extracted_symbol}' for query '{query}', but it is not a valid format.")
                return None
        except Exception as e:
            logger.error(f"An error occurred during Gemini API call for query interpretation ('{query}'): {e}", exc_info=True)
            return None

    def run(self, user_query):
        """
        Executes the agent's workflow: interprets the user's query and fetches the cryptocurrency price.
        
        Args:
            user_query (str): The user's input query.
            
        Returns:
            str: A formatted string with the cryptocurrency price, or an appropriate error/info message.
        """
        if not user_query or not user_query.strip():
            return "Please provide a query to get cryptocurrency prices (e.g., 'Bitcoin price')."

        try:
            logger.info(f"Running agent for user query: '{user_query}'")
            symbol = self.interpret_query(user_query)
            
            if symbol:
                price_result = self.get_crypto_price(symbol)
                
                # Check if price_result is a float (successful price) or a string (error message)
                if isinstance(price_result, float):
                    # Format the price nicely, e.g., $65,432.1234
                    return f"The current price of {symbol} is ${price_result:,.4f}"
                else:
                    # price_result is an error message string
                    logger.error(f"Failed to get price for {symbol}: {price_result}")
                    return f"I could determine the symbol as '{symbol}', but there was an issue fetching its price: {price_result}"
            else:
                logger.warning(f"No valid cryptocurrency symbol could be determined from query: '{user_query}'")
                return "I couldn’t determine the cryptocurrency you’re asking about. Please be more specific (e.g., 'What is Bitcoin?', 'Price of ETHUSDT')."
        except Exception as e:
            logger.error(f"An unexpected error occurred in agent.run for query '{user_query}': {e}", exc_info=True)
            return f"An unexpected internal issue occurred: {str(e)}. Please try again."

