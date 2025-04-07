from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ForwardRef, Optional, Type

from slackle.core.app import Slackle
from slackle.types.payload import SlackEvent
from slackle.types.response import SlackBlock, SlackMarkdown, SlackResponse


@dataclass
class SlackCommandMeta:
    command: str
    handler: Type["BaseSlackCommand"]
    description: str
    group: str
    visible: bool = True


class BaseSlackCommand(ABC):
    """
    Base class for all Slack commands.
    """

    description: str = ""
    group: str = "default"
    visible: bool = True

    @abstractmethod
    async def handle(
        self,
        text: str,
        user_id: str,
        app: Optional[Slackle] = None,
        event: Optional[SlackEvent] = None,
        **kwargs,
    ) -> str | SlackMarkdown | SlackBlock | SlackResponse:
        raise NotImplementedError("slack command handler must implement handle method")

    async def __call__(
        self,
        text: str,
        user_id: str,
        app: Optional[ForwardRef("Slackle")] = None,
        event: Optional[SlackEvent] = None,
        **kwargs,
    ) -> str | SlackMarkdown | SlackBlock:
        """
        return await self.handle(text, user_id, **kwargs)
        """
        return await self.handle(text, user_id, app=app, event=event, **kwargs)


__all__ = ["SlackCommandMeta", "BaseSlackCommand"]
