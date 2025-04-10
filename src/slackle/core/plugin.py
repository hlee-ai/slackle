"""
Slackle Plugin System

This module defines the base class for creating Slackle plugins, and
provides decorators for registering event hooks.

Plugins can register for lifecycle events like 'startup' or 'shutdown'
by using the `@on_slackle_event` decorator.

Example:

    from slackle.core.plugin import SlacklePlugin, on_slackle_event

    class MyPlugin(SlacklePlugin):
        @on_slackle_event("startup")
        async def on_startup(self, app):
            print("Plugin started!")
"""

import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Dict, List

if TYPE_CHECKING:
    from slackle.core.app import Slackle

# TODO: for now, hooks are only supported in plugins.
#  Create a decorator to register hooks in the app itself.
# TODO: add a feature to get plugin interface inside the app
#  for now plugin injects only indistinguishable attributes
#  this is not friendly for the user
#  user should be able to get plugin interface inside the app using keywords.


def on_slackle_event(event: str) -> Callable:
    """
    Decorator to mark a method as a handler for a named Slackle lifecycle event.

    Args:
        event (str): The name of the event to hook into (e.g., "startup", "shutdown").

    Returns:
        Callable: A decorator that registers the method for the event.
    """

    def decorator(func):
        func._slackle_event = event
        return func

    return decorator


class SlacklePlugin:
    """
    Base class for creating Slackle plugins.

    Subclass this to add custom behavior to your Slackle app. Plugins can register
    event hooks using the `@on_slackle_event` decorator, and can override the
    `setup(app)` method to add plugin-specific setup logic.

    Example:
        class MyPlugin(SlacklePlugin):
            def setup(self, app):
                app.register_plugin_attribute("my_plugin_data", {...})

            @on_slackle_event("startup")
            async def on_startup(self, app):
                ...
    """

    def __init__(self):
        self._event_hooks: Dict[str, List[Callable]] = defaultdict(list)
        self._collect_event_hooks()

    @property
    def name(self) -> str:
        """
        Returns the name of the plugin class.

        Returns:
            str: The name of the plugin, typically its class name.
        """
        return self.__class__.__name__

    def _collect_event_hooks(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_slackle_event"):
                event = getattr(attr, "_slackle_event")
                if attr not in self._event_hooks[event]:
                    self._event_hooks[event].append(attr)

    async def dispatch(self, app: "Slackle", event: str, **kwargs) -> None:
        """
        Dispatch a Slackle event to the plugin's registered event hooks.

        Args:
            app (Slackle): The Slackle app instance.
            event (str): The event name (e.g., "startup").
            **kwargs: Additional arguments to pass to the hook functions.
        """
        for hook in self._event_hooks.get(event, []):
            if asyncio.iscoroutinefunction(hook):
                await hook(self, app, **kwargs)
            else:
                hook(self, app, **kwargs)

    def setup(self, app: "Slackle") -> None:
        """
        Optional setup logic for the plugin.

        This method is called when the plugin is added to the Slackle app.

        Args:
            app (Slackle): The main Slackle app instance.
        """
        pass


__all__ = ["SlacklePlugin"]
