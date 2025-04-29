class AccountConnectionError(Exception):
    """Exception raised for errors in connecting to a Account client."""

    def __init__(self, message="Error connecting to Account client"):
        self.message = message
        super().__init__(self.message)


class AccountGetPortfolioInfoError(Exception):
    """Exception raised for errors in getting a portfolio from a Account client."""

    def __init__(self, message="Error getting portfolio from Account client"):
        self.message = message
        super().__init__(self.message)


class AccountPlaceOrderError(Exception):
    """Exception raised for errors in placing an order with a Account client."""

    def __init__(self, message="Error placing order with Account client"):
        self.message = message
        super().__init__(self.message)


class AccountGetInstrumentError(Exception):
    """Exception raised for errors in getting an instrument from a Account client."""

    def __init__(self, message="Error getting instrument from Account client"):
        self.message = message
        super().__init__(self.message)


class AccountGetOrderError(Exception):
    """Exception raised for errors in getting an order from a Account client."""

    def __init__(self, message="Error getting order from Account client"):
        self.message = message
        super().__init__(self.message)


class AccountCancelOrderError(Exception):
    """Exception raised for errors in cancelling an order with a Account client."""

    def __init__(self, message="Error cancelling order with Account client"):
        self.message = message
        super().__init__(self.message)
