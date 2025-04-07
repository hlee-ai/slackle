from typing import TYPE_CHECKING, List

from slackle.core.plugin import SlacklePlugin

if TYPE_CHECKING:
    from slackle.core.app import Slackle

# TODO: for now, hooks are only supported in plugins.
#  Create a decorator to register hooks in the app itself.


class HookDispatcher:
    def __init__(self, plugins: List[SlacklePlugin]):
        self._plugins = plugins

    async def emit(self, app: "Slackle", hook_name: str, **kwargs):
        for plugin in self._plugins:
            await plugin.dispatch(app, hook_name, **kwargs)


__all__ = ["HookDispatcher"]
