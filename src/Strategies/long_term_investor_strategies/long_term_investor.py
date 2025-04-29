from decimal import Decimal
import datetime
from Models.contract import Contract
from Models.portfolio import Portfolio
from clients.market_data_clients.base_market_data_client import BaseMarketDataClient
from clients.storage_clients.base_storage_client import BaseStorageClient
from clients.account_clients.base_account_client import BaseAccountClient
from strategies.base_strategy import BaseStrategy


class PeriodicInvestor(BaseStrategy):
    def __init__(
        self,
        trading_client: BaseAccountClient,
        storage_client: BaseStorageClient,
        market_data_client: BaseMarketDataClient,
        strategy_id: str = None,
        initialQuantity: Decimal = None,
        initialContract: Contract = None,
        initialPortfolio: Portfolio = None,
        tradeInterval: int = None,
        **kwargs,
    ):
        super().__init__(
            trading_client,
            storage_client,
            market_data_client,
            strategy_id,
            initialQuantity,
            initialContract,
            initialPortfolio,
        )

    def start(self):
        super().start()
        while self.is_running:
            ...

    def stop(self):
        super().stop()
