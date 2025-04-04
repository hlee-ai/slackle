from typing import TYPE_CHECKING

from starlette.requests import Request

if TYPE_CHECKING:
    from slackle.core.app import Slackle
    from slackle.plugins.formatter import Formatter
    from slackle.plugins.command import SlackCommand

def get_app(request: Request) -> "Slackle":
    return request.app

def get_formatter(request: Request) -> "Formatter":
    return request.app.formatter_registry

def get_command_registry(request: Request) -> "SlackCommand":
    return request.app.command_registry

__all__ = ['get_app', 'get_formatter', 'get_command_registry']