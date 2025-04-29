import docker

import logging 
logger = logging.getLogger(__name__)

from Config import IBKR_REST_CONTAINER_IMAGE, NETWORK_NAME, ACCOUNT_CONTAINER_PREFIX


class DockerClient:
    def __init__(self) -> None:
        self.connect()

    def connect(self):
        try:
            self.client = docker.from_env()
            data = self.client.images.list(name="*ibeam*")
            if not data:
                self.client.images.pull(IBKR_REST_CONTAINER_IMAGE, tag="latest")
                logger.info(f"Pulled {IBKR_REST_CONTAINER_IMAGE} image")
            logger.info(f"Connected to docker successfully")


        except Exception as e:
            logger.error(f"Error connecting to docker: {e}")
            raise e

    async def create_container(self, id,  account_name: str, username: str, password: str):
        if not account_name:
            raise ValueError("Container name cannot be empty")
        # return await self.dockerClient.containers.create(image=IBKR_REST_CONTAINER_IMAGE, detach=True, environment={"IBEAM_ACCOUNT": accountUser, "IBEAM_PASSWORD": accountPassword}, name="account_client_" + self.id)
        return await self.client.containers.create(image=IBKR_REST_CONTAINER_IMAGE, detach=True, environment={"IBEAM_ACCOUNT": username, "IBEAM_PASSWORD": password}, name= ACCOUNT_CONTAINER_PREFIX + id, network=NETWORK_NAME)
        # return await self.dockerClient.containers.create(image=IBKR_REST_CONTAINER_IMAGE, detach=True, environment={"IBEAM_ACCOUNT": accountUser, "IBEAM_PASSWORD": accountPassword, "IBEAM_KEY": KEY_BYTES}, name="account_client_" + self.id, network=NETWORK_NAME)
            
    def get_containers(self, prefix, all=True):
        return self.client.containers.list(all=all, filters={"name":prefix + "*"})

containerClient = DockerClient()