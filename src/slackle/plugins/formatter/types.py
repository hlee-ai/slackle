from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar

from slackle.constants import SlackResponseType
from slackle.types.response import SlackBlock, SlackMarkdown, SlackResponse

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
            raise TypeError(
                f"{self.__class__.__name__}"
                f" expects {self.data_type.__name__},"
                f" got {type(data).__name__}"
            )
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
    def to_slack_markdown(self) -> SlackMarkdown:
        """Return Slack markdown format."""
        raise NotImplementedError("Formatter must implement to_slack_markdown method")

    def to_plain_text(self) -> str:
        """Return plain text format."""
        return str(self.data)

    def to_slack_block(self) -> SlackBlock:
        """Return a Slack-compatible block object."""
        return SlackBlock(
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": self.to_slack_markdown().text},
                }
            ]
        )

    def to_slack_response(self) -> SlackResponse:
        """Return a Slack-compatible response object."""
        return SlackResponse(
            blocks=self.to_slack_block(), response_type=SlackResponseType.EPHEMERAL
        )
