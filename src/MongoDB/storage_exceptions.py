class StorageConnectionError(Exception):
    """Exception raised for errors in connecting to a storage client."""

    def __init__(self, message="Error connecting to storage client"):
        self.message = message
        super().__init__(self.message)


class StorageWriteError(Exception):
    """Exception raised for errors in writing to a storage client."""

    def __init__(self, message="Error writing to storage client"):
        self.message = message
        super().__init__(self.message)


class StorageReadError(Exception):
    """Exception raised for errors in reading from a storage client."""

    def __init__(self, message="Error reading from storage client"):
        self.message = message
        super().__init__(self.message)


class StorageUpdateError(Exception):
    """Exception raised for errors in updating a storage client."""

    def __init__(self, message="Error updating storage client"):
        self.message = message
        super().__init__(self.message)


class StorageDeleteError(Exception):
    """Exception raised for errors in deleting from a storage client."""

    def __init__(self, message="Error deleting from storage client"):
        self.message = message
        super().__init__(self.message)
