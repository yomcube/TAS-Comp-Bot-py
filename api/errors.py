class AppError(Exception):
    """Base class for expected app errors."""
    pass


class NoActiveTaskError(AppError):
    """Raised when there is no active task."""
    pass


class SubmissionRetrievalError(AppError):
    """Raised when a submission cannot be retrieved."""
    pass


class ActiveTaskError(AppError):
    """Raised when a task is already active."""
    pass


class NoDeadlineError(AppError):
    """Raised when there is no deadline set for the task."""
    pass


class DeadlineInPastError(AppError):
    """Raised when the deadline is in the past."""
    pass


class NoTaskDescriptionError(AppError):
    """Raised when there is no task description available."""
    pass


class NoSubmissionChannelError(AppError):
    """Raised when the submission channel is not set."""
    pass


class InvalidRkgError(AppError):
    """Raised when an invalid RKG is provided."""
    pass


class NoSubmissionError(AppError):
    """Raised when there is no submission for a user."""
    pass


class ReminderLimitError(AppError):
    """Raised when the number of reminders exceeds the limit."""
    pass
