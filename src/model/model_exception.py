class NotFoundError(Exception):
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


class DatabaseConnectionError(Exception):
    def __init__(self, detail: str = "Database connection error"):
        self.detail = detail


class DuplicateEntryError(Exception):
    def __init__(self, detail: str = "Duplicate entry error"):
        self.detail = detail


class InvalidQueryError(Exception):
    def __init__(self, detail: str = "Invalid query error"):
        self.detail = detail
