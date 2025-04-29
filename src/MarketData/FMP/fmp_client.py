import logging
from requests import get

from clients.market_data_clients.base_market_data_client import BaseMarketDataClient
from config import MARKET_DATA_CLIENT

logger = logging.getLogger(__name__)


class FMPClient(BaseMarketDataClient):
    """
    Client for getting market data from Financial Modeling Prep.
    """

    name = "FMPClient"

    def __init__(self, **kwargs):
        self.base_url = "https://financialmodelingprep.com/api/v3/"

    def connect(self):
        # Test connection to FMP API
        logger.info("Connecting to FMP API")

        count = 0

        while True:
            try:
                ...

            except:
                ...

    def stock_data(self, symbol, start_date, end_date):
        # Get stock data, date format: YYYY-MM-DD
        logger.info(f"Getting stock data for {symbol}")

        count = 0
        while True:
            try:
                results = get(
                    self.base_url
                    + f"historical-price-full/{symbol}?from={start_date}&to={end_date}"
                ).json()

            except:
                ...
