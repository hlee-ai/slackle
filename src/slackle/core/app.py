"""
Slackle App
"""

from contextlib import contextmanager
from typing import Any, Callable, List, Optional, Type

from fastapi import FastAPI

from slackle.config import SlackleConfig
from slackle.core.plugin import SlacklePlugin

from .dispatcher import HookDispatcher
from .slack.client import SlackClient
from .slack.interface import SlackInterface


class Slackle(FastAPI):
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
        return self._config

    @property
    def slack(self) -> SlackClient:
        return self._slack.client

    @property
    def callback(self):
        return self._slack.callbacks

    @property
    def hooks(self) -> HookDispatcher:
        if not hasattr(self, "_hook_dispatcher"):
            raise RuntimeError("Hooks are not available before startup.")
        return self._hook_dispatcher

    def on_event(self, name: str):
        return self.callback.event(name)

    def on_command(self, name: str):
        return self.callback.command(name)

    def on_action(self, name: str):
        return self.callback.action(name)

    @contextmanager
    def _plugin_setup(self):
        self.__plugin_setup_mode = True
        yield
        self.__plugin_setup_mode = False

    def _attach_slack_routes(self):
        self.include_router(self._slack.get_payload_router(), prefix="/slack", tags=["slack"])

    async def _on_startup(self):
        # setup hook dispatcher
        self._hook_dispatcher = HookDispatcher(self._plugins)
        self.__booted = True
        await self._hook_dispatcher.emit(self, "startup")

    async def _on_shutdown(self):
        await self._hook_dispatcher.emit(self, "shutdown")
        self.__booted = False

    def list_plugins(self):
        return [plugin.__class__.__name__ for plugin in self._plugins]

    def register_plugin_attribute(self, name: str, value: Any, *, override: bool = False):
        if self.__booted:
            raise RuntimeError("Cannot register plugin after app startup.")
        if not self.__plugin_setup_mode:
            raise RuntimeError("register_plugin_attribute can only be called during plugin setup.")
        if hasattr(self, name) and not override:
            raise AttributeError(f"Attribute '{name}' already exists in app.")
        setattr(self, name, value)
        self._plugin_attrs[name] = value

    def register_plugin_method(self, name: str, method: Callable, *, override: bool = False):
        if self.__booted:
            raise RuntimeError("Cannot register plugin method after app startup.")
        if not self.__plugin_setup_mode:
            raise RuntimeError("register_plugin_method can only be called during plugin setup.")
        if hasattr(self, name) and not override:
            raise AttributeError(f"Method '{name}' already exists in app.")
        setattr(self, name, method)
        self._plugin_attrs[name] = method

    def add_plugin(self, plugin: Type[SlacklePlugin]):
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
