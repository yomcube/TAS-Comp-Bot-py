class AppError(Exception):
    """Base class for expected app errors."""
    pass

class NoActiveTaskError(AppError):
    pass

class SubmissionRetrievalError(AppError):
    pass