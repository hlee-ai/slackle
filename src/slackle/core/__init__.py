"""
Slackle Core Package

Contains the building blocks of the Slackle framework, including:
- Slackle app container
- plugin system
- lifecycle hook dispatcher
- Slack integration stack (in `core.slack`)
"""

from .app import Slackle
from .dispatcher import HookDispatcher
from .plugin import SlacklePlugin

__all__ = [
    "Slackle",
    "SlacklePlugin",
    "HookDispatcher",
]
