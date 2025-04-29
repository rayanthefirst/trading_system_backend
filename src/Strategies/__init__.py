# Test Strategy
from strategies.test_strategy import TestStrategy

# Trailing Strategies
from strategies.trailing_strategies.long_buy_sell_trail import LongBuySellTrail
from strategies.trailing_strategies.long_short_buy_sell_trail import (
    LongShortBuySellTrail,
)
from strategies.trailing_strategies.short_sell_buy_trail import ShortSellBuyTrail
from strategies.trailing_strategies.long_short_neutral_buy_sell_trail import (
    LongShortNeutralBuySellTrail,
)

STRATEGIES = {
    TestStrategy.name: TestStrategy,
    LongBuySellTrail.name: LongBuySellTrail,
    LongShortBuySellTrail.name: LongShortBuySellTrail,
    ShortSellBuyTrail.name: ShortSellBuyTrail,
    LongShortNeutralBuySellTrail.name: LongShortNeutralBuySellTrail,
}
