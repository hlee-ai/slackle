"""
slack command registry
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from slackle.core.app import Slackle

from collections import defaultdict
from typing import Dict, Iterator, List, Optional, Type

from slackle.exc import CommandNotFoundError

from .dependencies import handle_command_with_dependencies
from .types import BaseSlackCommand, SlackCommandMeta


class SlackCommand:
    def __init__(self):
        self._registry: Dict[str, SlackCommandMeta] = {}

    def __contains__(self, command: str) -> bool:
        return command in self._registry

    def __getitem__(self, command: str) -> BaseSlackCommand:
        meta = self._registry.get(command)
        if not meta:
            raise CommandNotFoundError(f"No command registered for '{command}'")
        return meta.handler()

    def __iter__(self) -> Iterator[str]:
        return iter(self._registry)

    def __len__(self) -> int:
        return len(self._registry)

    def __repr__(self):
        return f"<SlackCommand commands={list(self._registry.keys())}>"

    def __str__(self):
        return f"<SlackCommand {len(self)} commands>"

    def register_meta(self, meta: SlackCommandMeta):
        self._registry[meta.command] = meta

    def register(
        self,
        command: str,
        description: Optional[str] = None,
        group: Optional[str] = None,
        visible: bool = True,
    ):
        """
        Decorator to register a Slack command handler class.

        Example:
            @command.register("/help", description="help", group="default")
            class HelpCommand(BaseSlackCommand):
                ...
        """

        def decorator(cls: Type[BaseSlackCommand]) -> Type[BaseSlackCommand]:
            if not issubclass(cls, BaseSlackCommand):
                raise TypeError("Registered class must subclass BaseSlackCommand")

            desc = description or getattr(cls, "description", "")
            grp = group or getattr(cls, "group", "")
            self._registry[command] = SlackCommandMeta(
                command=command,
                handler=cls,
                description=desc,
                group=grp,
                visible=visible,
            )
            return cls

        return decorator

    def hidden_command(
        self,
        command: str,
        description: Optional[str] = None,
        group: Optional[str] = None,
    ):
        return self.register(command, description=description, group=group, visible=False)

    def unregister(self, command: str) -> None:
        self._registry.pop(command, None)

    def get(self, command: str) -> Optional[BaseSlackCommand]:
        meta = self._registry.get(command)
        if meta:
            return meta.handler()
        return None

    def all(self) -> List[SlackCommandMeta]:
        return list(self._registry.values())

    def visible_commands(self) -> List[SlackCommandMeta]:
        return [meta for meta in self._registry.values() if meta.visible]

    def group_map(self) -> Dict[str, List[SlackCommandMeta]]:
        result = defaultdict(list)
        for meta in self._registry.values():
            result[meta.group].append(meta)
        return dict(result)

    def update_from(self, other: "SlackCommand") -> None:
        """
        Merge another SlackCommand registry into this one.
        """
        for meta in other.all():
            self._registry[meta.command] = meta

    async def dispatch(self, command: str, text: str, user_id: str, app: "Slackle") -> str:
        meta = self._registry.get(command)
        if not meta:
            return f"No command registered for '{command}'"

        return await handle_command_with_dependencies(meta.handler, app, text, user_id)


__all__ = ["SlackCommand"]
