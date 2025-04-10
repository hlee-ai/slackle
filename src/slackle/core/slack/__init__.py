"""
Slack core integration package.

This package provides the main components for handling Slack interactions in Slackle:
- SlackClient: A wrapper around Slack's AsyncWebClient
- SlackPayloadHandler: Routes and dispatches incoming Slack payloads
- SlackCallbackRegistry: Manages registered event/command/action callbacks
- SlackInterface: The unified entry point used in the Slackle app
"""

from .callback import SlackCallbackRegistry
from .client import SlackClient
from .handler import SlackPayloadHandler
from .interface import SlackInterface

__all__ = [
    "SlackCallbackRegistry",
    "SlackClient",
    "SlackPayloadHandler",
    "SlackInterface",
]
