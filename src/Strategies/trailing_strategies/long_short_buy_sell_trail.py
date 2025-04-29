from strategies.trailing_strategies.long_short_neutral_buy_sell_trail import (
    LongShortNeutralBuySellTrail,
)

import logging

logger = logging.getLogger(__name__)


class LongShortBuySellTrail(LongShortNeutralBuySellTrail):
    """
    Initially sets both a buy and sell trail and can go long or short,
    then it buys or sells with double the quantity to go short or long. Uses Margin.
    """

    name = "LongShortBuySellTrail"

    def get_new_quantity(self):
        return self.quantity * 2
