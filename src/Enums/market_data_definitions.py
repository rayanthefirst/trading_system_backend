from enum import Enum


class IntradayCandlestickGranularity(Enum):
    ONE_MINUTE = "1 min"
    FIVE_MINUTES = "5 min"
    FIFTEEN_MINUTES = "15 min"
    THIRTY_MINUTES = "30 min"
    ONE_HOUR = "1 hour"
    FOUR_HOURS = "4 hours"
    DAILY = "Daily"
