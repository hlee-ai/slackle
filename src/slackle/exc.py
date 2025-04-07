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


class ChannelNotFoundError(SlackleError):
    """Raised when a channel is not found in the registry."""

    def __init__(self, channel_id: str):
        super().__init__(f"Channel with ID '{channel_id}' not found")


class SlackResponseError(SlackleError):
    """Raised when there is an error in the Slack response."""

    def __init__(self, message: str):
        super().__init__(f"Slack response error: {message}")


class SlackleInitializationError(SlackleError):
    """Raised when there is an error during Slackle initialization."""

    def __init__(self, message: str):
        super().__init__(f"Slackle initialization error: {message}")
