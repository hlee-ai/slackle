from typing import Any, Iterator, Protocol


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


class SlackCallback:
    """
    A class for managing Slack event callbacks.
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
        return self._callbacks.get(callback)

    def has(self, callback: str) -> bool:
        return callback in self._callbacks

    def update_from(self, other: "SlackCallback"):
        """
        Update the current callback registry with another callback registry.
        """
        self._callbacks.update(other._callbacks)
        self._events.update(other._events)
        self._commands.update(other._commands)
        self._actions.update(other._actions)

    @classmethod
    def merge(cls, *callbacks: "SlackCallback") -> "SlackCallback":
        merged = cls()
        for cb in callbacks:
            merged.update_from(cb)
        return merged

    def event(self, event_type: str):
        def decorator(func: SlackCallbackHandler):
            self._callbacks[f"events:{event_type}"] = func
            self._events[event_type] = func
            return func

        return decorator

    def command(self, command_name: str):
        def decorator(func: SlackCallbackHandler):
            self._callbacks[f"command:{command_name}"] = func
            self._commands[command_name] = func
            return func

        return decorator

    def action(self, action_id: str):
        def decorator(func: SlackCallbackHandler):
            self._callbacks[f"interactivity:{action_id}"] = func
            self._actions[action_id] = func
            return func

        return decorator

    # TODO: add more decorators for different types of callbacks
