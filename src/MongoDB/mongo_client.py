import logging
import time

from pymongo.mongo_client import MongoClient as MG
from Enums.order_definitions import OrderState, OrderAction
from Enums.strategy_definitions import StrategyStatus
from Models.contract import Contract

from Utils.cipher import encrypt_str, decrypt_str

from .storage_exceptions import (
    StorageConnectionError,
    StorageWriteError,
    StorageReadError,
    StorageUpdateError,
    StorageDeleteError,
)

from Config import (
    MONGO_CONNECTION_STRING,
    MONGO_DATABASE,
    MONGO_DATABASE_COLLECTION_ORDER_DATA,
    MONGO_DATABASE_COLLECTION_STRATEGY_DATA,
    MONGO_DATABASE_COLLECTION_ACCOUNT_DATA,
    SLEEP_SECONDS,
    RETRY_COUNT,
)

logger = logging.getLogger(__name__)


class MongoClient():
    name = "MongoClient"

    def __init__(self, **kwargs):
        self.connect()
        
    def connect(self):
        # Connect to the Mongo database
        count = 0
        while True:
            try:
                uri = MONGO_CONNECTION_STRING
                self.client = MG(uri)
                self.client.admin.command("ping")

                self.db = self.client[MONGO_DATABASE]
                self.orderCollection = self.db[MONGO_DATABASE_COLLECTION_ORDER_DATA]
                self.strategyCollection = self.db[MONGO_DATABASE_COLLECTION_STRATEGY_DATA]
                self.accountCollection = self.db[MONGO_DATABASE_COLLECTION_ACCOUNT_DATA]

            except Exception:
                logger.error(f"Error connecting to storage client: {self.name}")
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                logger.info("Connected to Mongo database successfully")
                break

            if count == RETRY_COUNT:
                logger.critical(
                    f"Critical error connecting to storage client: {self.name}"
                )
                raise StorageConnectionError

    def disconnect(self):
        # Disconnect from the Mongo database
        pass

    def write(self, collection, **data):
        # Write data to the Mongo database
        count = 0
        while True:
            try:
                collection.insert_one(data)

            except Exception:
                logger.error("Error writing to Mongo database")
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                logger.debug("Data written to Mongo database successfully")
                break

            if count == RETRY_COUNT:
                logger.critical("Critical error writing to Mongo database")
                raise StorageWriteError

    def read(self, collection, **data):
        # Read data from the Mongo database
        count = 0
        while True:
            try:
                resultData = collection.find(data)

            except Exception:
                logger.error("Error reading from Mongo database")
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                logger.debug("Data read from Mongo database successfully")
                return resultData

            if count == RETRY_COUNT:
                logger.critical("Error reading from Mongo database")
                raise StorageReadError

    def write_order(
        self,
        strategy_id,
        order_id,
        contract: Contract,
        quantity,
        action: OrderAction,
        executedPrice,
        lastExecutedTime: int,
        orderState: OrderState,
        **kwargs,
    ):
        # Save the order to the database, lastExecutedTime is UTC timestamp in ms
        self.write(
            self.orderCollection,
            strategy_id=strategy_id,
            order_id=order_id,
            contract={
                "symbol": contract.symbol,
                "secType": contract.secType.value,
                "strike": contract.strike,
                "expiryDate": contract.expiryDate,
                "right": contract.right.value if contract.right else None,
            },
            quantity=quantity,
            action=action.value,
            executedPrice=executedPrice,
            lastExecutedTime=lastExecutedTime,
            orderState=orderState.value,
            **kwargs,
        )

    def update_order_state(self, strategy_id, order_id, newOrderState: OrderState):
        # Update the order state in the database
        count = 0
        while True:
            try:
                self.orderCollection.update_one(
                    {"strategy_id": strategy_id, "order_id": order_id},
                    {"$set": {"orderState": newOrderState.value}},
                )

            except Exception:
                logger.error("Error updating order state in Mongo database")
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                logger.debug("Order state updated in Mongo database successfully")
                break

            if count == RETRY_COUNT:
                logger.critical("Critical error updating order state in Mongo database")
                raise StorageUpdateError

    def check_for_active_orders(self, strategy_id):
        return list(
            self.read(
                self.orderCollection,
                strategy_id=strategy_id,
                orderState=OrderState.SUBMITTED.value,
            )
        )

    def get_all_strategies(self):
        return list(self.read(self.strategyCollection))

    def write_strategy(
        self, strategy_id, strategy_name, strategy_status: StrategyStatus, **kwargs
    ):
        self.write(
            self.strategyCollection,
            strategy_id=strategy_id,
            strategy_name=strategy_name,
            strategy_status=strategy_status.value,
            **kwargs,
        )

    def update_strategy_status(self, strategy_id, strategy_status: StrategyStatus):
        count = 0
        while True:
            try:
                self.strategyCollection.update_one(
                    {"strategy_id": strategy_id},
                    {"$set": {"strategy_status": strategy_status.value}},
                )

            except Exception:
                logger.error("Error updating strategy status in Mongo database")
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                logger.debug("Strategy status updated in Mongo database successfully")
                break

            if count == RETRY_COUNT:
                logger.critical(
                    "Critical error updating strategy status in Mongo database"
                )
                raise StorageUpdateError

    def remove_strategy(self, strategy_id):
        count = 0
        while True:
            try:
                self.strategyCollection.delete_one({"strategy_id": strategy_id})

            except Exception:
                logger.error("Error removing strategy from Mongo database")
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                logger.debug("Strategy removed from Mongo database successfully")
                break

            if count == RETRY_COUNT:
                logger.critical("Critical error removing strategy from Mongo database")
                raise StorageDeleteError

    def get_all_accounts(self):
        return list(self.read(self.accountCollection))

    def write_account(self, trading_client_name, account_type, trading_client_id, **kwargs):
        self.write(self.accountCollection, 
                   trading_client_name=trading_client_name,
                   account_type=account_type,
                   trading_client_id=trading_client_id,
                   **kwargs
                   )

    def remove_account(self, trading_client_id):
        count = 0
        while True:
            try:
                self.accountCollection.delete_one({"trading_client_id": trading_client_id})

            except Exception:
                logger.error("Error removing account from Mongo database")
                time.sleep(SLEEP_SECONDS)
                count += 1

            else:
                logger.debug("Account removed from Mongo database successfully")
                break

            if count == RETRY_COUNT:
                logger.critical("Critical error removing account from Mongo database")
                raise StorageDeleteError
            


mongoClient = MongoClient()