from fastapi import APIRouter

from decimal import Decimal

from config import strategy_handler

from clients.storage_clients import STORAGE_CLIENTS
from clients.account_clients import ACCOUNT_CLIENTS
from clients.market_data_clients import MARKET_DATA_CLIENTS

from Models.portfolio import Portfolio
from Models.contract import Contract

from Enums.securities_definitions import TradableSecurity, OptionSide


strategyRouter = APIRouter()




@strategyRouter.get("/available_strategies")
async def get_available_strategies():
    return strategy_handler.get_all_available_strategies()


@strategyRouter.get("/signature/{strategy_name}")
async def get_strategy_signature(strategy_name: str):
    return strategy_handler.get_strategy_signature(strategy_name)


@strategyRouter.get("/get_clients")
async def get_placed_strategies():
    return strategy_handler.get_placed_strategies()


@strategyRouter.get("/start_strategy/{strategy_id}")
async def start_strategy(strategy_id: str):
    return strategy_handler.start_strategy(strategy_id)


@strategyRouter.get("/stop_strategy/{strategy_id}")
async def stop_strategy(strategy_id: str):
    return strategy_handler.stop_strategy(strategy_id)


@strategyRouter.post("/create")
async def create_strategy(strategy_name: str, strategy_params: dict):

    trading_client = TRADING_CLIENTS[strategy_params.get("trading_client")]()
    storage_client = STORAGE_CLIENTS[strategy_params.get("storage_client")]()
    market_data_client = MARKET_DATA_CLIENTS[strategy_params.get("market_data_client")]()

    initialQuantity = (
        Decimal(strategy_params.get("initialQuantity"))
        if strategy_params.get("initialQuantity")
        else None
    )

    for security in TradableSecurity:
        if security.value == strategy_params.get("secType"):
            secType = security
            break

    strike = (
        Decimal(strategy_params.get("strike"))
        if strategy_params.get("strike")
        else None
    )

    for side in OptionSide:
        if side.value == strategy_params.get("right"):
            side = side

    initialContract = Contract(
        strategy_params.get("symbol"),
        secType,
        strike,
        strategy_params.get("expiryDate"),
        side,
    )

    cashBalance = (
        Decimal(strategy_params.get("cashBalance"))
        if strategy_params.get("cashBalance")
        else None
    )

    initialPortfolio = Portfolio(cashBalance=cashBalance)

    strategy_params["trading_client"] = trading_client
    strategy_params["storage_client"] = storage_client
    strategy_params["market_data_client"] = market_data_client
    strategy_params["initialQuantity"] = initialQuantity

    strategy_params["initialContract"] = initialContract
    strategy_params["initialPortfolio"] = initialPortfolio

    return strategy_handler.create_strategy(strategy_name, **strategy_params)


@strategyRouter.delete("/delete_strategy/{strategy_id}")
async def delete_strategy(strategy_id: str):
    return strategy_handler.delete_strategy(strategy_id)


