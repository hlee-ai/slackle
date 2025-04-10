"""
Slack Interface Module

This module provides the SlackInterface class, which serves as a wrapper
around the Slack client and payload handler. It initializes the Slack client
and provides methods for including callbacks and accessing the payload handler's internal router.
It also provides properties to access the Slack client and handler.
Slackle app uses this interface to interact with Slack's API and handle incoming payloads.
"""

from typing import Optional

from .callback import SlackCallbackRegistry
from .client import SlackClient
from .handler import SlackPayloadHandler


class SlackInterface:
    """
    Slack Interface

    This class serves as a wrapper around the Slack client and payload handler.
    It initializes the Slack client and provides methods for including callbacks
    and accessing the payload handler's internal router.
    It also provides properties to access the Slack client and handler.

    Properties:
        client (SlackClient): The Slack client instance.
        handler (SlackPayloadHandler): The Slack payload handler instance.
        callbacks (SlackCallbackRegistry): Registry for all registered callbacks.
    """

    def __init__(self, token: str):
        self.token = token
        self._client: Optional[SlackClient] = None  # slack client instance
        self._handler: Optional[SlackPayloadHandler] = None  # slack
        self._initialize()

    @property
    def client(self) -> SlackClient:
        """
        Return the Slack client instance.
        """
        if self._client is None:
            raise ValueError("Slack client has not been initialized.")
        return self._client

    @property
    def handler(self) -> SlackPayloadHandler:
        """
        Return the Slack payload handler instance.
        """
        if self._handler is None:
            raise ValueError("Slack payload handler has not been initialized.")
        return self._handler

    @property
    def callbacks(self) -> SlackCallbackRegistry:
        """
        Return the Slack callback registry instance.
        """
        if self._handler is None:
            raise ValueError("Slack payload handler has not been initialized.")
        return self._handler.callbacks

    def _initialize(self):
        """
        Initialize the Slack client and payload handler.
        """
        self._client = SlackClient(self.token)
        self._handler = SlackPayloadHandler()

    def include_callback(self, callback: SlackCallbackRegistry):
        """
        Include a callbacks to the Slack payload handler.

        Args:
            callback (SlackCallbackRegistry): The callback registry to include.

        Raises:
            TypeError: If the callback is not an instance of SlackCallbackRegistry.
        """
        if not isinstance(callback, SlackCallbackRegistry):
            raise TypeError("Expected a SlackCallbackRegistry instance.")
        self._handler.include_callback(callback)

    def get_payload_router(self):
        """
        Get the payload router from the Slack payload handler.

        Returns:
            APIRouter: The payload router instance.
        """
        return self._handler.router


__all__ = ["SlackInterface"]
