from Config import FASTAPI_HOST, FASTAPI_LOG_LEVEL, FASTAPI_PORT, FASTAPI_ENV
# Logging
import logging
import Utils.logging_settings
logger = logging.getLogger(__name__)
logger.info(f"Starting sever in {FASTAPI_ENV} environment")

# MongoDB
from MongoDB.mongo_client import mongoClient

# Docker
from Containerization.Docker.docker_client import containerClient

# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from APIRoutes.MainRouter import mainRouter
app.include_router(mainRouter)


if __name__ == "__main__":
    if FASTAPI_ENV == "prod":
        uvicorn.run("Server:app", port=FASTAPI_PORT, log_level=FASTAPI_LOG_LEVEL, reload=False, host=FASTAPI_HOST)
    elif FASTAPI_ENV == "dev":
        uvicorn.run("Server:app", port=FASTAPI_PORT, log_level=FASTAPI_LOG_LEVEL, reload=True, host=FASTAPI_HOST)
