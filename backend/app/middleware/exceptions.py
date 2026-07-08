class AppError(Exception):
    status_code = 500
    message = "Internal server error"

    def __init__(self, message: str | None = None, status_code: int | None = None):
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


class ValidationError(AppError):
    status_code = 400
    message = "Invalid request"


class NotFoundError(AppError):
    status_code = 404
    message = "Resource not found"


class StorageError(AppError):
    status_code = 502
    message = "Object storage operation failed"
