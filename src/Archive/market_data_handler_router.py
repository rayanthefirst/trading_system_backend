from fastapi import APIRouter
from config import market_data_handler

marketDataRouter = APIRouter()

@marketDataRouter.get("/get_market_data_client_types")
async def get_market_data_client_types():
    return market_data_handler.get_market_data_client_types()