from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, Optional, Type


class BaseSlackCommand(ABC):
    """
    Base class for all Slack commands.
    """
    description: str = ""

    @abstractmethod
    def handle(self, text: str, user_id: str) -> str:
        raise NotImplementedError("slack command handler must implement handle method")


T = TypeVar("T")
P = TypeVar("P", bound=Any)

class BaseFormatter(ABC, Generic[T, P]):
    """
    Base class for all formatters.
    - T: data type to format
    - P: parameters for the formatter
    """
    data_type: Type[T]

    def __init__(self, data: Any, parameters: Optional[P] = None):
        if not isinstance(data, self.data_type):
            raise TypeError(f"{self.__class__.__name__} expects data of type {self.data_type.__name__}, got {type(data).__name__}")
        self.data: T = self.clean(data)
        self.parameters: P = parameters or self.default_params()

    @classmethod
    @abstractmethod
    def default_params(cls) -> P:
        """Return default parameters for the formatter."""
        ...

    @staticmethod
    def clean(data: T) -> T:
        """Clean or validate the input data if necessary."""
        return data

    @abstractmethod
    def to_slack_markdown(self) -> str:
        """Return Slack markdown format."""
        raise NotImplementedError("Formatter must implement to_slack_markdown method")

    def to_plain_text(self) -> str:
        """Return plain text format."""
        return str(self.data)

    def to_slack_object(self) -> dict:
        """Return a Slack-compatible block object."""
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": self.to_slack_markdown()
            }
        }
