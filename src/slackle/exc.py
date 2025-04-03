# slackle/exc.py

class SlackleError(Exception):
    """Base exception for all Slackle-related errors."""
    pass

class CommandNotFoundError(SlackleError):
    """Raised when a Slack command is not found in the registry."""
    def __init__(self, command: str):
        super().__init__(f"No command registered for '{command}'")

class FormatterNotFoundError(SlackleError):
    """Raised when a formatter for a given data type is not found."""
    def __init__(self, data_type: type):
        super().__init__(f"No formatter registered for {data_type}")
