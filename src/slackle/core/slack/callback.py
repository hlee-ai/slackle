"""
Slack Callback System

This module defines the Slack callback protocol and registry class used to register
handlers for Slack events, commands, and interactive actions.
Slackle uses this system to manage the callbacks that respond to various Slack events.

The `SlackCallbackHandler` protocol defines the expected interface for a callback.
The `SlackCallbackRegistry` class manages all registered callbacks and provides decorators
such as `.event()`, `.command()`, and `.action()` for handler registration.
"""

from typing import Any, Callable, Iterator, Protocol


class SlackCallbackHandler(Protocol):
    """
    Protocol for a Slack event callback handler.

    Implement this protocol with an async function that accepts arbitrary keyword arguments.
    The event dispatcher will inject only the arguments your handler declares,
    based on the event context.

    Common available keyword arguments include:
    - `app`: the Slackle app instance
    - `slack`: the SlackClient wrapper
    - `payload`: raw SlackPayload object
    - `user_id`: the ID of the user who triggered the event
    - `channel_id`: the ID of the channel where the event occurred
    - `request`: the FastAPI request object
    - `response`: the FastAPI response object
    - ...and more depending on the event type.
    """

    async def __call__(self, **kwargs: Any) -> None: ...


class SlackCallbackRegistry:
    """
    Registry for Slack event, command, and interactivity callbacks.

    This class is used internally by Slackle to store and manage callback handlers
    for different types of Slack payloads. It also provides decorators to register
    handlers in a convenient way.

    Registered handlers can later be dispatched by the Slack interface layer.

    Decorators:
        - event(event_type): Register a Slack event handler (e.g., "app_mention").
        - command(command_name): Register a slash command handler (e.g., "/hello").
        - action(action_id): Register an interactivity handler (e.g., button ID).

    Properties:
        - callbacks: All registered callbacks.
        - events: Registered event handlers.
        - commands: Registered command handlers.
        - actions: Registered action handlers.
    """

    def __init__(self):
        self._callbacks: dict[str, SlackCallbackHandler] = {}
        self._events: dict[str, SlackCallbackHandler] = {}
        self._commands: dict[str, SlackCallbackHandler] = {}
        self._actions: dict[str, SlackCallbackHandler] = {}
        # TODO: add more callback types

    @property
    def callbacks(self) -> dict[str, SlackCallbackHandler]:
        return self._callbacks

    @property
    def events(self) -> dict[str, SlackCallbackHandler]:
        return self._events

    @property
    def commands(self) -> dict[str, SlackCallbackHandler]:
        return self._commands

    @property
    def actions(self) -> dict[str, SlackCallbackHandler]:
        return self._actions

    def __contains__(self, callback: str) -> bool:
        return callback in self._callbacks

    def __getitem__(self, callback: str) -> SlackCallbackHandler:
        handler = self._callbacks.get(callback)
        if not handler:
            raise KeyError(f"No callback registered for '{callback}'")
        return handler

    def __iter__(self) -> Iterator[str]:
        return iter(self._callbacks)

    def __len__(self) -> int:
        return len(self._callbacks)

    def __repr__(self):
        return f"<Callback callbacks={list(self._callbacks.keys())}>"

    def __str__(self):
        return f"<Callback {len(self)} callbacks>"

    def get(self, callback: str) -> SlackCallbackHandler | None:
        """
        Retrieve a registered callback handler by its name.

        Args:
            callback (str): The name of the callback to retrieve.

        Returns:
            SlackCallbackHandler | None: The registered callback handler, or None if not found.
        """
        return self._callbacks.get(callback)

    def has(self, callback: str) -> bool:
        """
        Check if a callback is registered in the registry.

        Args:
            callback (str): The name of the callback to check.

        Returns:
            bool: True if the callback is registered, False otherwise.
        """
        return callback in self._callbacks

    def update_from(self, other: "SlackCallbackRegistry") -> None:
        """
        Update the current registry with callbacks from another SlackCallbackRegistry.

        Args:
            other (SlackCallbackRegistry): The other registry to merge into this one.
        """
        self._callbacks.update(other._callbacks)
        self._events.update(other._events)
        self._commands.update(other._commands)
        self._actions.update(other._actions)

    @classmethod
    def merge(cls, *callbacks: "SlackCallbackRegistry") -> "SlackCallbackRegistry":
        """
        Merge multiple SlackCallbackRegistry instances into one.

        Useful when combining callbacks from multiple plugins or modules.

        Args:
            *callbacks: Any number of SlackCallbackRegistry instances.

        Returns:
            SlackCallbackRegistry: A new instance containing merged callback registries.
        """
        merged = cls()
        for cb in callbacks:
            merged.update_from(cb)
        return merged

    def event(self, event_type: str) -> Callable:
        """
        Register a handler for a Slack event.

        Args:
            event_type (str): The Slack event type to listen for (e.g., "app_mention").

        Returns:
            Callable: A decorator to register the event handler.
        """

        def decorator(func: SlackCallbackHandler):
            self._callbacks[f"events:{event_type}"] = func
            self._events[event_type] = func
            return func

        return decorator

    def command(self, command_name: str) -> Callable:
        """
        Register a handler for a Slack slash command.

        Args:
            command_name (str): The command string (e.g., "/hello").

        Returns:
            Callable: A decorator to register the command handler.
        """

        def decorator(func: SlackCallbackHandler):
            self._callbacks[f"command:{command_name}"] = func
            self._commands[command_name] = func
            return func

        return decorator

    def action(self, action_id: str) -> Callable:
        """
        Register a handler for a Slack interactive component action.

        Args:
            action_id (str): The action ID from a Slack interactive component.

        Returns:
            Callable: A decorator to register the action handler.
        """

        def decorator(func: SlackCallbackHandler):
            self._callbacks[f"interactivity:{action_id}"] = func
            self._actions[action_id] = func
            return func

        return decorator

    # TODO: add more decorators for different types of callbacks


__all__ = ["SlackCallbackHandler", "SlackCallbackRegistry"]
