import logging

from clients.market_data_clients import MARKET_DATA_CLIENTS

from config import MARKET_DATA_CLIENT

logger = logging.getLogger(__name__)


class MarketDataHandler:
    def __init__(self) -> None:
        logger.info("Initializing market data handler")
        self.market_data_clients = []
        self.default_market_data_client = MARKET_DATA_CLIENTS[MARKET_DATA_CLIENT]()
        
    
    def get_market_data_client(self, market_data_client_name: str, **kwargs):
        return MARKET_DATA_CLIENTS[market_data_client_name](**kwargs)
    
    def get_default_market_data_client(self):
        return self.default_market_data_client