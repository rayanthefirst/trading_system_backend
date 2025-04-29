from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Portfolio:
    cashBalance: Decimal
    # currency: str
    numberOfTransactions: int = 0
