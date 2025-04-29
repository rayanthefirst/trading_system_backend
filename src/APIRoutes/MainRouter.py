from fastapi import APIRouter

# from routers.market_data_handler_router import marketDataRouter
# from routers.storage_handler_router import storageRouter
# from routers.strategy_handler_router import strategyRouter
from .AccountRoutes.AccountRouter import accountRouter


mainRouter = APIRouter()


# mainRouter.include_router(strategyRouter, prefix="/strategy")
mainRouter.include_router(accountRouter, prefix="/accounts")
# mainRouter.include_router(marketDataRouter, prefix="/market_data")
# mainRouter.include_router(storageRouter, prefix="/storage")
