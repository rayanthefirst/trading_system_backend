from fastapi import APIRouter
from config import storage_client_handler

storageRouter = APIRouter()


@storageRouter.get("/get_storage_client_types")
async def get_storage_client_types():
    return storage_client_handler.get_storage_client_types()
