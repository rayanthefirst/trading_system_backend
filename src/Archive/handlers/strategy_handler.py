import logging
import inspect
from typing import List

from Enums.strategy_definitions import StrategyStatus

from strategies import STRATEGIES
from handlers.market_data_handler import MarketDataHandler
from handlers.account_client_handler import AccountClientHandler
from handlers.storage_client_handler import StorageClientHandler

from config import TRADING_CLIENT, MARKET_DATA_CLIENT, STORAGE_CLIENT


from strategies.base_strategy import BaseStrategy
from clients.storage_clients.base_storage_client import BaseStorageClient

logger = logging.getLogger(__name__)

storage_client = StorageClientHandler()
trading_client = AccountClientHandler(storage_client.get_default_storage_client())
market_data_client = MarketDataHandler()

class StrategyHandler:
    def __init__(self, storage_client: BaseStorageClient):
        self.storage_client = storage_client
        self.strategies: List[BaseStrategy] = []
        self.load_strategies()

    def load_strategies(self):
        """Load all strategies from storage client"""
        logger.info("Loading strategies from storage client")

        for strategy in self.storage_client.get_all_strategies():
            strategy["trading_client"] = trading_client.get_trading_client(strategy.get("trading_client_name", TRADING_CLIENT))
            strategy["market_data_client"] = market_data_client.get_market_data_client(strategy.get("market_data_client_name", MARKET_DATA_CLIENT))
            strategy["storage_client"] = storage_client.get_storage_client(strategy.get("storage_client_name", STORAGE_CLIENT))
            strategy: BaseStrategy = STRATEGIES[strategy["strategy_name"]](**strategy)
            self.strategies.append(strategy)

    def get_all_available_strategies(self):
        return list(STRATEGIES.keys())

    def get_placed_strategies(self):
        return [
            {
                "strategy_id": strategy.strategy_id,
                "strategy_name": strategy.name,
                "strategy_status": StrategyStatus.ACTIVE.value
                if strategy.is_running
                else StrategyStatus.INACTIVE.value,
            }
            for strategy in self.strategies
        ]

    def get_strategy_signature(self, strategy_name: str):
        signature = inspect.signature(STRATEGIES[strategy_name])
        param_names = [param.name for param in signature.parameters.values()]
        return param_names

    def start_strategy(self, strategy_id):
        strategy = self.get_strategy(strategy_id)
        if strategy == None:
            logger.error("Strategy not found")
            return f"Strategy {strategy_id} not found"
        elif strategy.is_running:
            logger.error("Strategy is already running")
            return f"Strategy {strategy_id} is already running"
        strategy.start()
        self.storage_client.update_strategy_status(strategy_id, StrategyStatus.ACTIVE)
        return f"Strategy {strategy_id} started"

    def stop_strategy(self, strategy_id):
        strategy = self.get_strategy(strategy_id)
        if strategy == None:
            logger.error("Strategy not found")
            return f"Strategy {strategy_id} not found"
        elif not strategy.is_running:
            logger.error("Strategy is not running")
            return f"Strategy {strategy_id} is not running"
        strategy.stop()
        self.storage_client.update_strategy_status(strategy_id, StrategyStatus.INACTIVE)
        return f"Strategy {strategy_id} stopped"

    def create_strategy(self, strategy_name, **kwargs):
        strategy: BaseStrategy = STRATEGIES[strategy_name](**kwargs)
        self.storage_client.write_strategy(
            strategy.strategy_id, strategy_name, StrategyStatus.INACTIVE
        )
        self.strategies.append(strategy)
        return strategy.strategy_id

    def delete_strategy(self, strategy_id):
        strategy = self.get_strategy(strategy_id)
        strategy.stop()
        self.strategies.remove(strategy)
        self.storage_client.remove_strategy(strategy_id)
        return f"Strategy {strategy_id} deleted"

    def get_strategy(self, strategy_id):
        for strategy in self.strategies:
            if strategy.strategy_id == strategy_id:
                return strategy
            

