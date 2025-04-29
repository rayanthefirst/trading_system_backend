from abc import ABC, abstractmethod
from clients.account_clients.base_account_client import BaseAccountClient
from clients.storage_clients.base_storage_client import BaseStorageClient
from clients.market_data_clients.base_market_data_client import BaseMarketDataClient

from Models.contract import Contract
from Models.portfolio import Portfolio

from decimal import Decimal
from uuid import uuid4


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies
    Strategy specific functions will be implemented in the derived class
    """

    name = "BaseStrategy"

    def __init__(
        self,
        trading_client: BaseAccountClient,
        storage_client: BaseStorageClient,
        market_data_client: BaseMarketDataClient,
        strategy_id: str = None,
        initialQuantity: Decimal = None,
        initialContract: Contract = None,
        initialPortfolio: Portfolio = None,
        **kwargs,
    ):
        self.trading_client = trading_client
        self.storage_client = storage_client
        self.market_data_client = market_data_client

        self.quantity = initialQuantity
        self.contract = initialContract
        self.portfolio = initialPortfolio

        self.strategy_id = strategy_id or str(uuid4())
        self.is_running = False
        
        self.lastFilledOrder = None

    @abstractmethod
    def start(self):
        self.is_running = True
        # Implement your strategy logic here

    @abstractmethod
    def stop(self):
        self.is_running = False
        # Implement any cleanup logic here

    @abstractmethod
    def get_strategy_info(self):
        # Implement logic to retrieve trade information
        pass

    @abstractmethod
    def get_new_quantity(self):
        pass

    @abstractmethod
    def get_new_contract(self):
        pass

    @abstractmethod
    def get_new_portfolio(self):
        pass
