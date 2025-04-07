from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any, Optional, Type

from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import solve_dependencies
from fastapi.requests import Request

from slackle.types.payload import SlackEvent

from .types import BaseSlackCommand

if TYPE_CHECKING:
    from slackle.core.app import Slackle


async def handle_command_with_dependencies(
    command_cls: Type[BaseSlackCommand],
    app: "Slackle",
    text: str,
    user_id: str,
    event: Optional[SlackEvent] = None,
) -> Any:
    command_instance = command_cls()
    method = getattr(command_instance, "handle")
    dependant = Dependant(call=method, path="")

    # dummy request
    request = Request(scope={"type": "http"})

    async with AsyncExitStack() as stack:
        values, _ = await solve_dependencies(
            request=request,
            dependant=dependant,
            dependency_overrides_provider=app,
            async_exit_stack=stack,
            embed_body_fields=True,
        )

    return await method(
        text=text,
        user_id=user_id,
        app=app,
        event=event,
        **values,
    )
