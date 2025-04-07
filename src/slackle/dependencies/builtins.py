from typing import TYPE_CHECKING

from starlette.requests import Request

if TYPE_CHECKING:
    from slackle.core.app import Slackle


def get_app(request: Request) -> "Slackle":
    return request.app


# TODO: add a function to get plugin inside app

__all__ = ["get_app"]
