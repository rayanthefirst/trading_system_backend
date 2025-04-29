"""
Defines the enums for securities
"""
from enum import Enum


class TradableSecurity(Enum):
    STOCK = "stock"
    OPTION = "option"
    FOREX = "forex"


class OptionSide(Enum):
    CALL = "call"
    PUT = "put"
