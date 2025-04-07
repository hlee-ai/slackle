from typing import Optional

from .callback import SlackCallback
from .client import SlackClient
from .handler import SlackPayloadHandler


class SlackInterface:
    def __init__(self, token: str):
        self.token = token
        self._client: Optional[SlackClient] = None  # slack client instance
        self._handler: Optional[SlackPayloadHandler] = None  # slack
        self._initialize()

    @property
    def client(self) -> SlackClient:
        if self._client is None:
            raise ValueError("Slack client has not been initialized.")
        return self._client

    @property
    def handler(self) -> SlackPayloadHandler:
        if self._handler is None:
            raise ValueError("Slack payload handler has not been initialized.")
        return self._handler

    @property
    def callbacks(self) -> SlackCallback:
        if self._handler is None:
            raise ValueError("Slack payload handler has not been initialized.")
        return self._handler.callbacks

    def _initialize(self):
        self._client = SlackClient(self.token)
        self._handler = SlackPayloadHandler()

    def include_callback(self, callback: SlackCallback):
        """
        Include a callbacks to the Slack payload handler.
        """
        if not isinstance(callback, SlackCallback):
            raise TypeError("Expected a SlackCallback instance.")
        self._handler.include_callback(callback)

    def get_payload_router(self):
        """
        Get the payload router from the Slack payload handler.
        """
        return self._handler.router
