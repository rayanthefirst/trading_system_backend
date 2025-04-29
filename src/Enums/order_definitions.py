"""
Contains definitions for enums used for Orders not the contract
"""
from enum import Enum


class OrderAction(Enum):
    BUY = "buy"
    SELL = "sell"


class TrailingStopType(Enum):
    AMOUNT = "amount"
    PERCENTAGE = "percentage"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop limit"
    TRAILING_STOP = "trailing stop"
    TRAILING_STOP_LIMIT = "trailing stop limit"


class OrderState(Enum):
    PENDING_SUBMIT = "pending submit"
    PENDING_CANCEL = "pending cancel"
    PRE_SUBMITTED = "pre submitted"
    SUBMITTED = "submitted"
    CANCELLED = "cancelled"
    FILLED = "filled"
    INACTIVE = "inactive"


class OrderTIF(Enum):
    DAY = "day"
    GOOD_TILL_CANCELLED = "good till cancelled"
