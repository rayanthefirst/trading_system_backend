import logging

from config import STORAGE_CLIENT
from clients.storage_clients import STORAGE_CLIENTS

logger = logging.getLogger(__name__)



class StorageClientHandler:
    def __init__(self) -> None:
        logger.info("Initializing storage client handler")
        self.storage_clients = []
        self.default_storage_client = STORAGE_CLIENTS[STORAGE_CLIENT]()
        self.storage_clients.append(self.default_storage_client)


    def get_storage_client_types(self):
        return list(STORAGE_CLIENTS.keys())

    def get_storage_client(self, storage_client_name: str, **kwargs):
        return STORAGE_CLIENTS[storage_client_name](**kwargs)
    
    def get_default_storage_client(self):
        return self.default_storage_client
        
