from decimal import Decimal
import time
from Models.contract import Contract
from Models.portfolio import Portfolio
from clients.market_data_clients.base_market_data_client import (
    BaseMarketDataClient,
)
from clients.storage_clients.base_storage_client import BaseStorageClient
from clients.account_clients.base_account_client import BaseAccountClient
from strategies.base_strategy import BaseStrategy

from Enums.order_definitions import (
    OrderState,
    OrderAction,
    OrderTIF,
    TrailingStopType,
)

from config import SLEEP_SECONDS

import logging

logger = logging.getLogger(__name__)


class BaseTrail(BaseStrategy):
    """
    Base class for trailing strategies
    """

    name = "BaseTrail"

    def __init__(
        self,
        trading_client,
        storage_client,
        market_data_client,
        strategy_id=None,
        initialQuantity=None,
        initialContract=None,
        initialPortfolio=None,
        initialTrlAmtOrPrc: Decimal = None,
        initialTrlType: TrailingStopType = None,
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

        self.trlAmtOrPrc = initialTrlAmtOrPrc
        self.trlType = initialTrlType

    def start(self):
        logger.info(f"Starting strategy: {self.name}, id: {self.strategy_id}")
        self.is_running = True

    def stop(self):
        self.is_running = False

    def check_and_wait_for_active_orders(self):
        activeOrders = self.storage_client.check_for_active_orders(self.strategy_id)
        # # If active order exists, wait till order is filled
        if len(activeOrders) != 0:
            logger.info("Active orders exist, waiting for order(s) to be fill")
            orderCompleted = False
            while not orderCompleted:
                for index, order in enumerate(activeOrders):
                    orderStatus = self.trading_client.get_order_status(
                        order["order_id"]
                    )
                    if orderStatus["status"] == OrderState.FILLED.value:
                        # Update order state in database and portfolio
                        self.storage_client.update_order_state(
                            self.strategy_id, order["order_id"], OrderState.FILLED
                        )
                        self.lastFilledOrder = order
                        activeOrders.pop(index)
                        orderCompleted = True
                        break
                    else:
                        time.sleep(SLEEP_SECONDS)

            # Cancel any remaining orders
            logger.info("Cancelling remaining orders")
            for order in activeOrders:
                self.trading_client.cancel_order(order["order_id"])
                self.storage_client.update_order_state(
                    self.strategy_id, order["order_id"], OrderState.CANCELLED
                )

    def get_strategy_info(self):
        pass

    def get_new_quantity(self):
        return self.quantity

    def get_new_trl_params(self):
        return self.trlAmtOrPrc, self.trlType

    def get_new_contract(self) -> Contract:
        return self.contract

    def get_new_portfolio(self) -> Portfolio:
        return self.portfolio

    def update_strategy(self):
        ...
