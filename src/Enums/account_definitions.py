from enum import Enum

class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class AccountType(Enum):
    MARGIN = "margin"
    NO_MARGIN = "no margin"