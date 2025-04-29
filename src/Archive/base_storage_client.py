from abc import ABC, abstractmethod
from Enums.order_definitions import OrderState, OrderAction
from Enums.strategy_definitions import StrategyStatus
from Models.contract import Contract


class BaseStorageClient(ABC):
    name = "BaseStorageClient"

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    # Order Methods
    @abstractmethod
    def write_order(
        self,
        strategy_id,
        order_id,
        contract: Contract,
        quantity,
        action: OrderAction,
        executedPrice,
        executedTime: int,  # Unix timestamp UTC in ms
        orderState: OrderState,
        **kwargs,
    ):
        pass

    @abstractmethod
    def update_order_state(self, strategy_id, order_id, newOrderState: OrderState):
        pass

    @abstractmethod
    def check_for_active_orders(self, strategy_id):
        """
        Check if there is any active orders for the strategy id and return it
        if not return empty list
        """
        pass
    
    # Strategy Methods
    @abstractmethod
    def get_all_strategies(self):
        """
        Get all strategies for the strategy handler
        """
        pass

    @abstractmethod
    def write_strategy(
        self, strategy_id, strategy_name, strategy_status: StrategyStatus, **kwargs
    ):
        pass

    @abstractmethod
    def update_strategy_status(self, strategy_id, strategy_status: StrategyStatus):
        pass

    @abstractmethod
    def remove_strategy(self, strategy_id):
        pass

    # Account Methods - Accounts will represent a single portfolio if an account has multiple portfolios
    @abstractmethod
    def get_all_accounts(self):
        """
        Get all accounts for the trading handler
        """
        pass

    @abstractmethod
    def write_account(self, trading_client_name, account_type, trading_client_id, **kwargs):
        pass

    @abstractmethod
    def remove_account(self, trading_client_id):
        pass
    