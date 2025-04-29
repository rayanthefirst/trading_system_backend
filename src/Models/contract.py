from dataclasses import dataclass
from decimal import Decimal
from Enums.securities_definitions import TradableSecurity, OptionSide


@dataclass
class Contract:
    symbol: str
    secType: TradableSecurity
    strike: Decimal = None
    expiryDate: str = None
    right: OptionSide = None
