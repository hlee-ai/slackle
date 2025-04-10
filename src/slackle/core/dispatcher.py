"""
Hook Dispatcher

This module defines the `HookDispatcher` class, which handles dispatching lifecycle
hooks (e.g., "startup", "shutdown") to registered Slackle plugins.

Currently, only plugins can register hooks. Support for app-level hooks may be added later.
"""

from typing import TYPE_CHECKING, List

from slackle.core.plugin import SlacklePlugin

if TYPE_CHECKING:
    from slackle.core.app import Slackle

# TODO: for now, hooks are only supported in plugins.
#  Create a decorator to register hooks in the app itself.


class HookDispatcher:
    """
    Dispatches named lifecycle hooks to all registered Slackle plugins.

    This class is used internally by the Slackle app to notify plugins when
    specific events occur, such as app startup or shutdown.

    Properties:
        plugins (List[SlacklePlugin]): The list of plugin instances to notify.
    """

    def __init__(self, plugins: List[SlacklePlugin]):
        self._plugins = plugins

    @property
    def plugins(self) -> List[SlacklePlugin]:
        """
        Returns the list of registered plugins.

        Returns:
            List[SlacklePlugin]: The list of registered plugins.
        """
        return self._plugins

    async def emit(self, app: "Slackle", hook_name: str, **kwargs):
        """
        Emit a lifecycle hook to all plugins that have registered for it.

        Args:
            app (Slackle): The main Slackle app instance.
            hook_name (str): The name of the hook to trigger (e.g., "startup").
            **kwargs: Any additional keyword arguments to pass to the plugin handlers.
        """
        for plugin in self._plugins:
            await plugin.dispatch(app, hook_name, **kwargs)


__all__ = ["HookDispatcher"]
