from abc import ABC, abstractmethod
import logging
from decimal import Decimal
from Enums.order_definitions import (
    OrderAction,
    OrderTIF,
    TrailingStopType,
)
from Enums.securities_definitions import TradableSecurity, OptionSide
from Enums.account_definitions import AccountType

import docker

from uuid import uuid4

logger = logging.getLogger(__name__)


class BaseAccountClient(ABC):
    """Abstract base class which encapsulates necessary functions from trading account platforms"""

    name = "BaseAccountClient"

    def __init__(self, alias, account_type: AccountType, **kwargs):
        self.alias = alias
        self.user = kwargs.get("username", "")
        self.account_type = account_type
        self.id = str(uuid4())
        self.dockerClient = docker.DockerClient()
        self.container =  None
        self.is_running = False

    @abstractmethod
    async def create_account_container(self):
        return None
    
    @abstractmethod
    def get_status(self):
        ...
    
    @abstractmethod
    async def connect(self):
        logger.info(f"Connecting to account client: {self.name}")
        self.is_running = True

    @abstractmethod
    def disconnect(self):
        self.is_running = False

    @abstractmethod
    def get_portfolio_info(self):
        """
        Example response:
        [{'position': Decimal('7614.6300000000001091393642127513885498046875'), 'currency': 'CAD', 'expiry': None, 'putOrCall': None, 'strike': Decimal('0'), 'assetClass': 'CASH', 'ticker': 'CAD'},
          {'position': Decimal('6971.59000000000014551915228366851806640625'), 'currency': 'USD', 'expiry': None, 'putOrCall': None, 'strike': Decimal('0'), 'assetClass': 'CASH', 'ticker': 'USD'}]
        """

    @abstractmethod
    def place_market_order(
        self,
        quantity: Decimal,
        action: OrderAction,
        timeInForce: OrderTIF,
        symbol: str,
        secType: TradableSecurity,
        expiryDate: str = None,
        strike: Decimal = None,
        right: OptionSide = None,
    ):
        ...

    @abstractmethod
    def place_trail_order(
        self,
        quantity: Decimal,
        action: OrderAction,
        timeInForce: OrderTIF,
        trlAmtOrPrc: Decimal,
        trlType: TrailingStopType,
        symbol: str,
        secType: TradableSecurity,
        expiryDate: str = None,
        strike: Decimal = None,
        right: OptionSide = None,
    ):
        ...

    @abstractmethod
    def get_order_status(self, orderId: int):
        """
        Example response:
        {'status': 'filled', 'executedPrice': Decimal('181.13'), 'executedTime': 1704488394000}
        """
        ...

    @abstractmethod
    def cancel_order(self, orderId: int):
        ...
