from Enums.order_definitions import (
    OrderState,
    OrderAction,
    OrderTIF,
)

from strategies.trailing_strategies.base_trail import BaseTrail
import logging

logger = logging.getLogger(__name__)


class ShortSellBuyTrail(BaseTrail):
    """
    Initially sets a sell trail and only goes short, then a buy trail on a
    stock (with margin - Quantity is same) and trails it. If stock price goes down or up
    by percentage or amount, trailing stop will be triggered.
    """

    name = "ShortSellBuyTrail"

    def start(self):
        super().start()

        while self.is_running:
            self.check_and_wait_for_active_orders()

            # Place new order
            if (
                self.lastFilledOrder == None
                or self.lastFilledOrder["side"] == OrderAction.BUY.value
            ):
                self.quantity = self.get_new_quantity()
                action = OrderAction.SELL
                newTrlAmtOrPrc, newTrlType = self.get_new_trl_params()
                self.contract = self.get_new_contract()

                # Place sell order
                logger.info("Placing sell trail order")
                newOrderId = self.trading_client.place_trail_order(
                    self.quantity,
                    action,
                    OrderTIF.GOOD_TILL_CANCELLED,
                    newTrlAmtOrPrc,
                    newTrlType,
                    self.contract.symbol,
                    self.contract.secType,
                    self.contract.expiryDate,
                    self.contract.strike,
                    self.contract.right,
                )

            elif self.lastFilledOrder["side"] == OrderAction.SELL.value:
                self.quantity = self.get_new_quantity()
                action = OrderAction.BUY
                newTrlAmtOrPrc, newTrlType = self.get_new_trl_params()
                self.contract = self.get_new_contract()

                # Place buy order
                logger.info("Placing buy trail order")
                newOrderId = self.trading_client.place_trail_order(
                    self.quantity,
                    action,
                    OrderTIF.GOOD_TILL_CANCELLED,
                    newTrlAmtOrPrc,
                    newTrlType,
                    self.contract.symbol,
                    self.contract.secType,
                    self.contract.expiryDate,
                    self.contract.strike,
                    self.contract.right,
                )

            # To be set later
            executedPrice = None
            executedTime = None

            # Save order to database and update portfolio
            logger.info("Saving order to database")
            self.storage_client.write_order(
                self.strategy_id,
                newOrderId,
                self.contract,
                self.quantity,
                action,
                executedPrice,
                executedTime,
                OrderState.SUBMITTED,
            )
