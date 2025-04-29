from strategies.base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)


class TestStrategy(BaseStrategy):
    name = "TestStrategy"

    def start(self):
        self.is_running = True
        logger.info(f"Starting strategy: {self.name}, id: {self.strategy_id}")

    def stop(self):
        self.is_running = False
        logger.info(f"Stopping strategy: {self.name}, id: {self.strategy_id}")

    def get_strategy_info(self):
        logger.info(f"Getting strategy info: {self.name}, id: {self.strategy_id}")

    def get_new_quantity(self):
        pass

    def get_new_contract(self):
        pass

    def get_new_portfolio(self):
        pass
