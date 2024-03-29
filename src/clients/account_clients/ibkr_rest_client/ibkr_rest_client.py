import calendar
import logging
import time
import warnings
from decimal import Decimal

# from cryptography.fernet import Fernet


from requests import Response, get, post, delete
from urllib3.exceptions import InsecureRequestWarning
from clients.account_clients.ibkr_rest_client.ibkr_definitions import (
    IBKRTradableSecurity,
    IBKROrderTIF,
    IBKRTrailingStopType,
)
from config import SLEEP_SECONDS, RETRY_COUNT, IBKR_REST_CONTAINER_IMAGE, NETWORK_NAME, KEY_BYTES, CONTAINER_START_DELAY
from definitions.order_definitions import (
    OrderAction,
    OrderTIF,
    TrailingStopType,
)
from definitions.securities_definitions import TradableSecurity, OptionSide
from definitions.account_definitions import AccountType, AccountStatus
from clients.account_clients.base_account_client import BaseTradingClient
from clients.account_clients.account_exceptions import (
    AccountConnectionError,
    AccountGetPortfolioInfoError,
    AccountPlaceOrderError,
    AccountGetInstrumentError,
    AccountGetOrderError,
    AccountCancelOrderError,
)

warnings.simplefilter("ignore", InsecureRequestWarning)

logger = logging.getLogger(__name__)

class IBKRRestClient(BaseTradingClient):
    name = "IBKRRestClient"

    def __init__(self, alias, user, password, account_type: AccountType, ibkrAccountId=None, trading_client_id=None, container=None, **kwargs):
        super().__init__(alias, account_type, trading_client_id, container, user=user, password=password, **kwargs)
        # self.encrpytionClient = Fernet(KEY_BYTES)
        self.accountId = ibkrAccountId
        self.host_url = f"https://trading_client_{self.trading_client_id}:5000/v1/api"

    def check_response(self, resp: Response) -> bool:
        if resp.status_code == 200:
            return True
        elif resp.status_code != 200:
            logger.error(f"IBKR REST Error: {resp.json()}")
            raise Exception(f"IBKR REST Error: {resp.json()['error']}")
        else:
            logger.error(f"Client Error: {resp.json()}")
            raise Exception(f"Client Error: {resp.json()['error']}")

    def ibkr_get_request(self, uri_path: str, params: dict = None) -> Response:
        resp = get(self.host_url + uri_path, params=params, verify=False)
        if self.check_response(resp):
            return resp.json()

    def ibkr_post_request(
        self, uri_path: str, body: dict = None, params: dict = None
    ) -> Response:
        resp = post(self.host_url + uri_path, json=body, params=params, verify=False)
        if self.check_response(resp):
            return resp.json()

    def ibkr_delete_request(
        self, uri_path: str, body: dict = None, params: dict = None
    ) -> Response:
        resp = delete(self.host_url + uri_path, json=body, params=params, verify=False)
        if self.check_response(resp):
            return resp.json()

    # ABSTRACT BASE CLASS METHODS
    def create_trading_client_container(self, **kwargs):
        accountUser = kwargs.get("user")
        accountPassword = kwargs.get("password")
        # return self.dockerClient.containers.create(image=IBKR_REST_CONTAINER_IMAGE, detach=True, environment={"IBEAM_ACCOUNT": accountUser, "IBEAM_PASSWORD": accountPassword}, name="trading_client_" + self.trading_client_id)
        return self.dockerClient.containers.create(image=IBKR_REST_CONTAINER_IMAGE, detach=True, environment={"IBEAM_ACCOUNT": accountUser, "IBEAM_PASSWORD": accountPassword}, name="trading_client_" + self.trading_client_id, network=NETWORK_NAME)
        # return self.dockerClient.containers.create(image=IBKR_REST_CONTAINER_IMAGE, detach=True, environment={"IBEAM_ACCOUNT": accountUser, "IBEAM_PASSWORD": accountPassword, "IBEAM_KEY": KEY_BYTES}, name="trading_client_" + self.trading_client_id, network=NETWORK_NAME)
        
    def connect(self):
        super().connect()
        self.container.start()
        time.sleep(CONTAINER_START_DELAY)
        try:
            while self.is_running:
                account_status = self.get_status()
                if account_status == AccountStatus.ACTIVE:
                    break
                time.sleep(SLEEP_SECONDS)
                
        except AccountConnectionError:
            self.disconnect()

        else:
            if account_status == AccountStatus.ACTIVE:
                self.accountId = self.get_trading_client_account_id()

            else:
                logger.critical("Critical error connecting to IBKR REST API")
                raise AccountConnectionError


    def disconnect(self):
        super().disconnect()
        self.container.stop()
        return self.get_status()


    def get_status(self):
        count = 0
        while self.is_running:
            try:
                authSessionResponse = post(self.host_url + "/iserver/auth/status", json={}, verify=False)

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
    

    def get_trading_client_account_id(self):
        count = 0
        while True:
            try:
                accountInfo = self.ibkr_get_request("/portfolio/accounts")
            
            except Exception:
                logger.error("Error getting account ID from IBKR REST API")
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                return accountInfo[0]["accountId"]
            
            if count == RETRY_COUNT:
                logger.critical("Critical error getting account ID from IBKR REST API")
                raise AccountGetPortfolioInfoError
                    
        
    def get_portfolio_info(self):
        count = 0
        while True:
            try:
                accountPositions = []
                paginationCount = 0
                while True:
                    accPos = self.ibkr_get_request(
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
        symbol = symbol.lower()
        conid = self.get_instrument_conid(symbol, secType, expiryDate, strike, right)
        logger.info(f"Placing market order")

        count = 0
        while True:
            try:
                createdOrder = self.ibkr_post_request(
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
                    return self.confirm_order(replyId)

            if count == RETRY_COUNT:
                logger.critical("Critical error placing market order")
                raise AccountPlaceOrderError

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
        symbol = symbol.lower()
        conid = self.get_instrument_conid(symbol, secType, expiryDate, strike, right)
        logger.info(f"Placing trail order")

        count = 0
        while True:
            try:
                createdOrder = self.ibkr_post_request(
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

    def confirm_order(self, replyId: str):
        logger.info(f"Confirming order")
        count = 0
        try:
            while True:
                confirmOrder = self.ibkr_post_request(
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

    def get_instrument_conid(
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
                symbolInfo = self.ibkr_post_request(
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
                    availableStrikes = self.ibkr_get_request(
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

                    for option in self.ibkr_get_request(
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

    def get_live_orders(self):
        count = 0
        while True:
            try:
                live_orders = self.ibkr_get_request("/iserver/account/orders")["orders"]

            except Exception:
                logger.error("Error getting live orders")
                time.sleep(SLEEP_SECONDS)
                count += 1
            else:
                return live_orders

            if count == RETRY_COUNT:
                logger.critical("Critical error getting live orders")
                raise AccountGetOrderError

    def get_order_status(self, orderId: int):
        count = 0
        while True:
            try:
                orders = self.get_live_orders()
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

    def cancel_order(self, orderId: int):
        count = 0
        while True:
            try:
                cancelled_order = self.ibkr_delete_request(
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
