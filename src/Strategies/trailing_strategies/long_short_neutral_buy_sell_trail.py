from strategies.trailing_strategies.base_trail import BaseTrail
from Enums.order_definitions import (
    OrderState,
    OrderAction,
    OrderTIF,
)


import logging

logger = logging.getLogger(__name__)


class LongShortNeutralBuySellTrail(BaseTrail):
    """
    Initially sets both a buy and sell trail and can go long or short,
    then it buys or sells with the quantity to go back to position balance of 0 then go short or long again. Uses Margin.
    """

    name = "LongShortNeutralBuySellTrail"

    def start(self):
        super().start()

        while self.is_running:
            self.check_and_wait_for_active_orders()

            # Place new order
            if self.lastFilledOrder == None:
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

            elif self.lastFilledOrder["side"] == OrderAction.BUY.value:
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
