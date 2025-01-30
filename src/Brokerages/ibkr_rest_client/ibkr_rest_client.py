import calendar
import logging
import time
import warnings
from decimal import Decimal

from requests import Response, get, post, delete
from urllib3.exceptions import InsecureRequestWarning
from .ibkr_definitions import (
    IBKRTradableSecurity,
    IBKROrderTIF,
    IBKRTrailingStopType,
)
from Config import SLEEP_SECONDS, RETRY_COUNT, IBKR_REST_CONTAINER_IMAGE, NETWORK_NAME, CONTAINER_START_DELAY, ACCOUNT_CONTAINER_PREFIX
from Enums.order_definitions import (
    OrderAction,
    OrderTIF,
    TrailingStopType,
)
from Enums.securities_definitions import TradableSecurity, OptionSide
from Enums.account_definitions import AccountType, AccountStatus
from ..base_account_client import BaseAccountClient
from ..account_exceptions import (
    AccountConnectionError,
    AccountGetPortfolioInfoError,
    AccountPlaceOrderError,
    AccountGetInstrumentError,
    AccountGetOrderError,
    AccountCancelOrderError,
)

warnings.simplefilter("ignore", InsecureRequestWarning)

logger = logging.getLogger(__name__)

class IBKRRestClient(BaseAccountClient):
    name = "IBKRRestClient"

    def __init__(self, alias, username, password, account_type: AccountType, **kwargs):
        super().__init__(alias, account_type, username=username, password=password, **kwargs)
        self.host_url = f"https://{ACCOUNT_CONTAINER_PREFIX}{self.id}:5000/v1/api"
        self.accountId = None # Set in connect method on client start

    def check_response(self, resp: Response) -> bool:
        if resp.status_code == 200:
            return True
        elif resp.status_code != 200:
            logger.error(f"IBKR REST Error: {resp.json()}")
            raise Exception(f"IBKR REST Error: {resp.json()['error']}")
        else:
            logger.error(f"Client Error: {resp.json()}")
            raise Exception(f"Client Error: {resp.json()['error']}")

    async def ibkr_get_request(self, uri_path: str, params: dict = None) -> Response:
        resp = await get(self.host_url + uri_path, params=params, verify=False)
        if self.check_response(resp):
            return resp.json()

    async def ibkr_post_request(
        self, uri_path: str, body: dict = None, params: dict = None
    ) -> Response:
        resp = await post(self.host_url + uri_path, json=body, params=params, verify=False)
        if self.check_response(resp):
            return resp.json()

    async def ibkr_delete_request(
        self, uri_path: str, body: dict = None, params: dict = None
    ) -> Response:
        resp = await delete(self.host_url + uri_path, json=body, params=params, verify=False)
        if self.check_response(resp):
            return resp.json()

    # ABSTRACT BASE CLASS METHODS
    async def create_account_container(self, **kwargs):
        ...
        
        
    async def connect(self):
        await super().connect()
        await self.container.start()
        time.sleep(CONTAINER_START_DELAY)
        try:
            while self.is_running:
                account_status = await self.get_status()
                if account_status == AccountStatus.ACTIVE:
                    break
                time.sleep(SLEEP_SECONDS)

        except AccountConnectionError:
            self.disconnect()

        else:
            if account_status == AccountStatus.ACTIVE:
                self.accountId = self.get_ibkr_account_id()

            else:
                logger.critical("Critical error connecting to IBKR REST API")
                raise AccountConnectionError


    async def disconnect(self):
        super().disconnect()
        await self.container.stop()
        return await self.get_status()


    async def get_status(self):
        count = 0
        while self.is_running:
            try:
                authSessionResponse = await post(self.host_url + "/iserver/auth/status", json={}, verify=False)

            except Exception as e:
                logger.error(f"Error connecting to IBKR REST API or Server: {e}")
                print(self.host_url)
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                if authSessionResponse.status_code != 200:
                    time.sleep(SLEEP_SECONDS)
                    continue
                
                if authSessionResponse.json()["authenticated"]:
                    logger.info("Checking IBKR REST API connection")
                    return AccountStatus.ACTIVE

            if count == RETRY_COUNT:
                logger.critical("Critical error connecting to IBKR REST API or Server")
                raise AccountConnectionError
        
        return AccountStatus.INACTIVE


    async def get_ibkr_account_id(self):
        count = 0
        while True:
            try:
                accountInfo = await self.ibkr_get_request("/portfolio/accounts")

            except Exception:
                logger.error("Error getting account ID from IBKR REST API")
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                return accountInfo[0]["accountId"]

            if count == RETRY_COUNT:
                logger.critical("Critical error getting account ID from IBKR REST API")
                raise AccountGetPortfolioInfoError

    
    async def get_portfolio_info(self):
        count = 0
        while True:
            try:
                accountPositions = []
                paginationCount = 0
                while True:
                    accPos = await self.ibkr_get_request(
                        f"/portfolio/{self.accountId}/positions/{paginationCount}"
                    )

                    if accPos == []:
                        break

                    accountPositions += [
                        {
                            "position": Decimal(pos["position"]),
                            "currency": pos["currency"],
                            "expiry": pos["expiry"],
                            "putOrCall": pos["putOrCall"],
                            "strike": Decimal(pos["strike"]),
                            "assetClass": pos["assetClass"],
                            "ticker": pos["ticker"],
                        }
                        # Default 30 pos per request
                        for pos in accPos
                        if pos["assetClass"]
                        != IBKRTradableSecurity[TradableSecurity.FOREX]
                    ]

                    paginationCount += 1

                accountCash = [
                    {
                        "position": Decimal(pos["cashbalance"]),
                        "currency": k,
                        "expiry": None,
                        "putOrCall": None,
                        "strike": Decimal(0),
                        "assetClass": "CASH",
                        "ticker": k,
                    }
                    for k, pos in self.ibkr_get_request(
                        f"/portfolio/{self.accountId}/ledger"
                    ).items()
                    if k != "BASE"
                ]

            except KeyError:
                time.sleep(SLEEP_SECONDS)
                continue
            except Exception:
                logger.error("Error getting portfolio info")
                time.sleep(SLEEP_SECONDS)
                count += 1
            else:
                return accountPositions + accountCash

            if count == RETRY_COUNT:
                logger.critical("Critical error getting portfolio info")
                raise AccountGetPortfolioInfoError

    async def place_market_order(
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
        symbol = symbol.lower()
        conid = await self.get_instrument_conid(symbol, secType, expiryDate, strike, right)
        logger.info(f"Placing market order")

        count = 0
        while True:
            try:
                createdOrder = await self.ibkr_post_request(
                    f"/iserver/account/{self.accountId}/orders",
                    body={
                        "orders": [
                            {
                                "conid": conid,
                                "orderType": "MKT",
                                "quantity": quantity,
                                "side": action.value,
                                "tif": IBKROrderTIF[timeInForce],
                            }
                        ]
                    },
                )
                createdOrder = createdOrder[0]

            except Exception:
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                if "order_id" in createdOrder:
                    return int(createdOrder["order_id"])
                else:
                    replyId = createdOrder["id"]
                    return await self.confirm_order(replyId)

            if count == RETRY_COUNT:
                logger.critical("Critical error placing market order")
                raise AccountPlaceOrderError

    async def place_trail_order(
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
        symbol = symbol.lower()
        conid = await self.get_instrument_conid(symbol, secType, expiryDate, strike, right)
        logger.info(f"Placing trail order")

        count = 0
        while True:
            try:
                createdOrder = await self.ibkr_post_request(
                    f"/iserver/account/{self.accountId}/orders",
                    body={
                        "orders": [
                            {
                                "conid": conid,
                                "orderType": "TRAIL",
                                "quantity": quantity,
                                "side": action.value,
                                "tif": IBKROrderTIF[timeInForce],
                                "trailingAmt": trlAmtOrPrc,
                                "trailingType": IBKRTrailingStopType[trlType],
                            }
                        ]
                    },
                )
                createdOrder = createdOrder[0]

            except Exception:
                logger.error("Error placing trail order")
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                if "order_id" in createdOrder:
                    return int(createdOrder["order_id"])
                else:
                    replyId = createdOrder["id"]
                    return self.confirm_order(replyId)

            if count == RETRY_COUNT:
                logger.critical("Critical error placing trail order")
                raise AccountPlaceOrderError

    async def confirm_order(self, replyId: str):
        logger.info(f"Confirming order")
        count = 0
        try:
            while True:
                confirmOrder = await self.ibkr_post_request(
                    f"/iserver/reply/{replyId}", body={"confirmed": True}
                )
                confirmOrder = confirmOrder[0]
                if "order_id" in confirmOrder:
                    return int(confirmOrder["order_id"])
                else:
                    replyId = confirmOrder["id"]

        except Exception:
            logger.error("Error confirming order")
            time.sleep(SLEEP_SECONDS)
            count += 1

        if count == RETRY_COUNT:
            logger.critical("Critical error confirming order")
            raise AccountPlaceOrderError

    async def get_instrument_conid(
        self,
        symbol: str,
        secType: TradableSecurity,
        expiryDate: str = None,
        strike: Decimal = None,
        right: OptionSide = None,
    ):
        """
        right: "call" or "put"
        Only works for STK and OPT
        """
        secType = IBKRTradableSecurity[secType]
        right = right.value if right else None

        count = 0
        while True:
            try:
                symbolInfo = await self.ibkr_post_request(
                    "/iserver/secdef/search", body={"symbol": symbol}
                )[0]
                underlyingConid = int(symbolInfo["conid"])
                if secType == IBKRTradableSecurity[TradableSecurity.OPTION]:
                    numericalFormattedDate = expiryDate.replace("-", "")
                    availableOptionDates = symbolInfo["opt"].split(";")

                    if numericalFormattedDate not in availableOptionDates:
                        raise AccountGetInstrumentError(
                            "No available option contract for expiry date"
                        )

                    monthYearFormattedDate = (
                        calendar.month_abbr[int(expiryDate[5:7])].upper()
                        + expiryDate[2:4]
                    )
                    availableStrikes = await self.ibkr_get_request(
                        "/iserver/secdef/strikes",
                        params={
                            "conid": underlyingConid,
                            "sectype": "OPT",
                            "month": monthYearFormattedDate,
                        },
                    )

                    if strike not in availableStrikes[right]:
                        raise AccountGetInstrumentError(
                            "No available option contract for strike price"
                        )

                    for option in await self.ibkr_get_request(
                        "/iserver/secdef/info",
                        params={
                            "conid": underlyingConid,
                            "sectype": "OPT",
                            "month": monthYearFormattedDate,
                            "strike": strike,
                            "right": "C" if right == "call" else "P",
                        },
                    ):
                        if option["maturityDate"] == numericalFormattedDate:
                            return int(option["conid"])

                elif secType == IBKRTradableSecurity[TradableSecurity.STOCK]:
                    return underlyingConid
            except Exception:
                logger.error("Error getting instrument conid")
                time.sleep(SLEEP_SECONDS)
                count += 1

            if count == RETRY_COUNT:
                logger.critical("Critical error getting instrument conid")
                raise AccountGetInstrumentError

    async def get_live_orders(self):
        count = 0
        while True:
            try:
                live_orders = await self.ibkr_get_request("/iserver/account/orders")["orders"]

            except Exception:
                logger.error("Error getting live orders")
                time.sleep(SLEEP_SECONDS)
                count += 1
            else:
                return live_orders

            if count == RETRY_COUNT:
                logger.critical("Critical error getting live orders")
                raise AccountGetOrderError

    async def get_order_status(self, orderId: int):
        count = 0
        while True:
            try:
                orders = await self.get_live_orders()
                for order in orders:
                    if order["orderId"] == orderId:
                        return {
                            "status": order["status"].lower(),
                            "executedPrice": None
                            if "avgPrice" not in order
                            else Decimal(order["avgPrice"]),
                            "lastExecutedTime": None
                            if "lastExecutionTime_r" not in order
                            else order["lastExecutionTime_r"],
                        }
                else:
                    return None

            except Exception:
                logger.error("Error getting order status")
                time.sleep(SLEEP_SECONDS)
                count += 1

            if count == RETRY_COUNT:
                logger.critical("Critical error getting order status")
                raise AccountGetOrderError

    async def cancel_order(self, orderId: int):
        count = 0
        while True:
            try:
                cancelled_order = await self.ibkr_delete_request(
                    f"/iserver/account/{self.accountId}/order/{orderId}"
                )
            except Exception:
                logger.error("Error cancelling order")
                time.sleep(SLEEP_SECONDS)
                count += 1
            else:
                return cancelled_order

            if count == RETRY_COUNT:
                logger.critical("Critical error cancelling order")
                raise AccountCancelOrderError
