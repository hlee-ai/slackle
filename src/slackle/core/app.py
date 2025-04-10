"""
Slackle App

This module defines the main `Slackle` class, which extends FastAPI to provide a convenient
interface for building Slack bots using Slackle.

It manages the Slack client, plugin system, and callback handlers,
and provides decorators for registering Slack events, slash commands, and interactive actions.

Typical usage:

    from slackle.core.app import Slackle

    app = Slackle()

    @app.on_command("/hello")
    async def handle_hello(app, slack, text, user_id, channel_id):
        return "Hello there!"
"""

from contextlib import contextmanager
from typing import Any, Callable, List, Optional, Type

from fastapi import FastAPI

from slackle.config import SlackleConfig
from slackle.core.plugin import SlacklePlugin

from .dispatcher import HookDispatcher
from .slack import SlackCallbackRegistry
from .slack.client import SlackClient
from .slack.interface import SlackInterface


class Slackle(FastAPI):
    """
    The main application class for building a Slack bot with Slackle.

    This class serves as the central entry point to the Slackle framework and extends FastAPI.
    It manages Slack callback registration, plugin integration, and Slack client communication.

    Properties:
        config (SlackleConfig): Configuration object containing Slack tokens and settings.
        slack (SlackClient): The Slack WebClient instance used for sending messages and API calls.
        callback: Dispatcher for Slack events, commands, and interactive actions.
        hooks (HookDispatcher): Hook system for handling app lifecycle events such as
        startup and shutdown.
    """

    def __init__(self, *, config: Optional[SlackleConfig] = None, **kwargs):
        super().__init__(**kwargs)

        # inner flags
        self.__plugin_setup_mode = False
        self.__booted = False

        # config
        self._config: SlackleConfig = config or SlackleConfig()

        # inner engines
        self._slack: SlackInterface = SlackInterface(self._config.app_token)
        self._plugins: List[SlacklePlugin] = []
        self._plugin_attrs = {}
        self._hook_dispatcher = HookDispatcher(self._plugins)

        # fastapi hooks
        self.add_event_handler("startup", self._on_startup)
        self.add_event_handler("shutdown", self._on_shutdown)

        # initialize slack routes
        self._attach_slack_routes()

    @property
    def config(self) -> SlackleConfig:
        """
        Return the configuration object for the Slackle app.
        """
        return self._config

    @property
    def slack(self) -> SlackClient:
        """
        Return the Slack client instance used for sending messages and API calls.
        """
        return self._slack.client

    @property
    def callback(self) -> SlackCallbackRegistry:
        """
        Return the callback registry for all registered callbacks.
        """
        return self._slack.callbacks

    @property
    def hooks(self) -> HookDispatcher:
        """
        Return the hook dispatcher for managing app lifecycle events.
        """
        if not hasattr(self, "_hook_dispatcher"):
            raise RuntimeError("Hooks are not available before startup.")
        return self._hook_dispatcher

    def on_event(self, name: str) -> Callable:
        """
        Register a Slack event handler.

        Args:
            name (str): The name of the Slack event to listen for (e.g., "app_mention").

        Returns:
            Callable: A decorator to register the event handler function.
        """
        return self.callback.event(name)

    def on_command(self, name: str) -> Callable:
        """
        Register a Slack slash command handler.

        Args:
            name (str): The name of the slash command (e.g., "/hello").

        Returns:
            Callable: A decorator to register the command handler function.
        """
        return self.callback.command(name)

    def on_action(self, name: str) -> Callable:
        """
        Register a Slack interactive action handler.
        Args:
            name (str): The name of the action (e.g., "button_click").

        Returns:
            Callable: A decorator to register the action handler function.
        """
        return self.callback.action(name)

    @contextmanager
    def _plugin_setup(self):
        """
        Context manager for setting up plugins.
        """
        self.__plugin_setup_mode = True
        yield
        self.__plugin_setup_mode = False

    def _attach_slack_routes(self):
        """
        Attach the Slack routes to Slackle app.
        """
        self.include_router(self._slack.get_payload_router(), prefix="/slack", tags=["slack"])

    async def _on_startup(self):
        """
        Emit the startup hook to all registered plugins.
        """
        self._hook_dispatcher = HookDispatcher(self._plugins)
        self.__booted = True
        await self._hook_dispatcher.emit(self, "startup")

    async def _on_shutdown(self):
        """
        Emit the shutdown hook to all registered plugins.
        """
        await self._hook_dispatcher.emit(self, "shutdown")
        self.__booted = False

    def list_plugins(self):
        """
        List all registered plugins.

        Returns:
            List[str]: A list of plugin names.
        """
        return [plugin.__class__.__name__ for plugin in self._plugins]

    def register_plugin_attribute(self, name: str, value: Any, *, override: bool = False):
        """
        Register an attribute for the plugin.

        Args:
            name (str): The name of the attribute.
            value (Any): The value of the attribute.
            override (bool): Whether to override an existing attribute. Defaults to False.

        Raises:
            RuntimeError: If called after the app has started.
            RuntimeError: If called outside of plugin setup mode.
            AttributeError: If the attribute already exists and override is False.
        """
        if self.__booted:
            raise RuntimeError("Cannot register plugin after app startup.")
        if not self.__plugin_setup_mode:
            raise RuntimeError("register_plugin_attribute can only be called during plugin setup.")
        if hasattr(self, name) and not override:
            raise AttributeError(f"Attribute '{name}' already exists in app.")
        setattr(self, name, value)
        self._plugin_attrs[name] = value

    def register_plugin_method(self, name: str, method: Callable, *, override: bool = False):
        """
        Register a method for the plugin.
        Args:
            name (str): The name of the method.
            method (Callable): The method to register.
            override (bool): Whether to override an existing method. Defaults to False.

        Raises:
            RuntimeError: If called after the app has started.
            RuntimeError: If called outside of plugin setup mode.
            AttributeError: If the method already exists and override is False.
        """
        if self.__booted:
            raise RuntimeError("Cannot register plugin method after app startup.")
        if not self.__plugin_setup_mode:
            raise RuntimeError("register_plugin_method can only be called during plugin setup.")
        if hasattr(self, name) and not override:
            raise AttributeError(f"Method '{name}' already exists in app.")
        setattr(self, name, method)
        self._plugin_attrs[name] = method

    def add_plugin(self, plugin: Type[SlacklePlugin]):
        """
        Register a plugin with the Slackle app.

        Args:
            plugin (Type[SlacklePlugin]): The plugin class to register.

        Raises:
            TypeError: If the plugin is not a subclass of SlacklePlugin.
            ValueError: If the plugin is already registered.
        """
        with self._plugin_setup():
            if not issubclass(plugin, SlacklePlugin):
                raise TypeError(
                    f"Plugin must be a subclass of SlacklePlugin, got {plugin.__name__}"
                )
            if plugin in self._plugins:
                raise ValueError(f"Plugin {plugin.__name__} is already registered.")
            _plugin = plugin()
            _plugin.setup(self)
            self._plugins.append(_plugin)


__all__ = ["Slackle"]
