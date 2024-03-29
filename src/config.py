import os
# General Settings
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS"))
RETRY_COUNT = int(os.getenv("RETRY_COUNT"))
KEY_BYTES = os.getenv("KEY").encode("utf-8")

# Logging Settings
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")
LOGGING_FROMADDR = os.getenv("LOGGING_FROMADDR")
LOGGING_TOADDR = os.getenv("LOGGING_TOADDR")
LOGGING_PASSWORD = os.getenv("LOGGING_PASSWORD")

# FastAPI Settings
FASTAPI_HOST = os.getenv("FASTAPI_HOST")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT"))
FASTAPI_LOG_LEVEL = os.getenv("FASTAPI_LOG_LEVEL")
FASTAPI_ENV = os.getenv("FASTAPI_ENV")

# Default Client Settings
TRADING_CLIENT = os.getenv("TRADING_CLIENT")
MARKET_DATA_CLIENT = os.getenv("MARKET_DATA_CLIENT")
STORAGE_CLIENT = os.getenv("STORAGE_CLIENT")

# Docker Settings
NETWORK_NAME = os.getenv("NETWORK_NAME")
IBKR_REST_CONTAINER_IMAGE = os.getenv("IBKR_REST_CONTAINER_IMAGE")
CONTAINER_START_DELAY = int(os.getenv("CONTAINER_START_DELAY"))


# MongoDB Client Settings
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")
MONGO_DATABASE_COLLECTION_ORDER_DATA = os.getenv("MONGO_DATABASE_COLLECTION_ORDER_DATA")
MONGO_DATABASE_COLLECTION_STRATEGY_DATA = os.getenv("MONGO_DATABASE_COLLECTION_STRATEGY_DATA")
MONGO_DATABASE_COLLECTION_ACCOUNT_DATA = os.getenv("MONGO_DATABASE_COLLECTION_ACCOUNT_DATA")

# FMP Client Settings
FMP_API_KEY = os.getenv("FMP_API_KEY")

# Initalize Handlers
from handlers.market_data_handler import MarketDataHandler
from handlers.storage_client_handler import StorageClientHandler
from handlers.strategy_handler import StrategyHandler
from handlers.trading_client_handler import TradingClientHandler

storage_client_handler = StorageClientHandler()
default_storage_client = storage_client_handler.get_default_storage_client()

market_data_handler = MarketDataHandler()
strategy_handler = StrategyHandler(default_storage_client)
trading_client_handler = TradingClientHandler(default_storage_client)

