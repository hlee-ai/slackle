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


# Define a decorator to register event handlers
def on_slackle_event(event: str):
    """
    Decorator to register a method as an event handler for Slackle events.
    """

    def decorator(func):
        func._slackle_event = event
        return func

    return decorator


class SlacklePlugin:
    def __init__(self):
        self._event_hooks: Dict[str, List[Callable]] = defaultdict(list)
        self._collect_event_hooks()

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def _collect_event_hooks(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_slackle_event"):
                event = getattr(attr, "_slackle_event")
                if attr not in self._event_hooks[event]:
                    self._event_hooks[event].append(attr)

    async def dispatch(self, app: "Slackle", event: str, **kwargs):
        for hook in self._event_hooks.get(event, []):
            if asyncio.iscoroutinefunction(hook):
                await hook(self, app, **kwargs)
            else:
                hook(self, app, **kwargs)

    def setup(self, app: "Slackle") -> None:
        """
        Setup method to initialize the plugin inside Slackle app.
        """
        pass
