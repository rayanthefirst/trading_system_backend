import logging
from typing import List
import inspect



from Containerization.Docker.docker_client import containerClient
from MongoDB.mongo_client import mongoClient

from Utils.cipher import encrypt_str, decrypt_str

from Brokerages.base_account_client import BaseAccountClient
from Brokerages import ACCOUNT_CLIENTS


from Config import ACCOUNT_CONTAINER_PREFIX



from Enums.account_definitions import AccountStatus, AccountType

logger = logging.getLogger(__name__)

class AccountHandler:
    def __init__(self) -> None:
        logger.info("Initializing trading client handler")
        self.trading_clients: List[BaseAccountClient] = []
        
        self.load_trading_clients()

    def load_trading_clients(self):
        for container in containerClient.get_containers(ACCOUNT_CONTAINER_PREFIX):
            container.stop()
            container.remove()

        for account in mongoClient.get_all_accounts():
            for accountType in AccountType:
                if accountType.value == account.get("account_type"):
                    account["account_type"] = accountType

        
            account["username"] = decrypt_str(account["username"])
            account["password"] = decrypt_str(account["password"])
            trading_client = ACCOUNT_CLIENTS[account["trading_client_name"]](**account)

            self.trading_clients.append(trading_client)        
            

    def get_trading_client_types(self):
        return list(ACCOUNT_CLIENTS.keys())
    
    def get_trading_client_signature(self, trading_client_name):
        signature = inspect.signature(ACCOUNT_CLIENTS[trading_client_name])
        param_names = [param.name for param in signature.parameters.values()]
        return param_names
        
    
    async def get_trading_clients(self):
        return [
            {   
                "name": trading_client.alias, 
                # "trading_client_account_user": encrypt_str(trading_client.user),
                "trading_client_type": trading_client.name,
                # "id": trading_client.id,
                "trading_client_account_type": trading_client.account_type.value,
                # "ibkrAccountId": trading_client.accountId if trading_client.accountId == None else encrypt_str(trading_client.accountId),
                "status": await self.get_trading_client_status(trading_client.id)
            } for trading_client in self.trading_clients
        ]

    def start_trading_client(self, id):
        trading_client = self.get_trading_client(id)
        trading_client.connect()

    def stop_trading_client(self, id):
        trading_client = self.get_trading_client(id)
        trading_client.disconnect()
        

    def create_trading_client(self, trading_client_name: str, **kwargs):
        encryptedUser = kwargs.get("user")
        encryptedPassword = kwargs.get("password")

        kwargs["user"] = decrypt_str(kwargs.get("user"))
        kwargs["password"] = decrypt_str(kwargs.get("password"))

        trading_client = ACCOUNT_CLIENTS[trading_client_name](**kwargs)
        self.trading_clients.append(trading_client)

        kwargs["user"] = encryptedUser
        kwargs["password"] = encryptedPassword

        mongoClient.write_account(trading_client_name,
                                        trading_client.account_type.value,
                                          trading_client.id,
                                          **{key:value for key, value in kwargs.items() if type(key) == str and type(value) == str}),
    
    
    def delete_trading_client(self, id: str):
        trading_client = self.get_trading_client(id)
        trading_client.disconnect()
        trading_client.container.remove()
        self.trading_clients.remove(trading_client)
        mongoClient.remove_account(trading_client.id)

    async def get_trading_client_status(self, id: str):
        trading_client = self.get_trading_client(id)
        return await trading_client.get_status()

    def get_trading_client(self, id: str):
        for trading_client in self.trading_clients:
            if trading_client.id == id:
                return trading_client



account_handler = AccountHandler()