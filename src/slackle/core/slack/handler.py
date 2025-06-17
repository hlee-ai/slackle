import inspect
from typing import TYPE_CHECKING, Annotated, Awaitable, Callable, Type

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from pydantic import BaseModel

from slackle.core.slack.callback import SlackCallback
from slackle.dependencies import get_app
from slackle.types.context import SlackleContext
from slackle.types.payload import (
    SlackCommandPayload,
    SlackEventPayload,
    SlackInteractionPayload,
    SlackPayload,
)

if TYPE_CHECKING:
    from slackle.core.app import Slackle


class SlackPayloadHandler:
    _ROUTES = [
        ("events", SlackEventPayload),
        ("command", SlackCommandPayload, True),
        ("interactivity", SlackInteractionPayload, True),
    ]

    def __init__(self):
        self._callback_registry: SlackCallback = SlackCallback()
        self.router = APIRouter()
        self._register_routes()

    @property
    def callbacks(self) -> SlackCallback:
        return self._callback_registry

    async def _pre_handle(
        self,
        handle_type: str,
        handle_name: str,
        app: "Slackle",
        request: Request,
        response: Response,
        payload: SlackPayload,
        context: SlackleContext,
    ):
        """
        Pre-handle the request before passing it to the handler.
        This is where you can add custom logic before the handler is called.
        """
        await app.hooks.emit(
            app,
            "slack.pre_handle",
            handle_type=handle_type,
            handle_name=handle_name,
            request=request,
            response=response,
            payload=payload,
            context=context,
        )

        if request.headers.get("X-Slack-Retry-Num") and app.config.ignore_retry_events:
            return context.skip("Ignoring retry events")

        if (
            payload.token != app.config.verification_token
            and not app.config.unsafe_turnoff_token_verification
        ):
            return context.skip("Ignoring invalid token")

        if handle_type == "events":
            event = payload.event
            if event.user == app.config.app_user_id:
                return context.skip("Ignoring self events")

            if app.config.ignore_bot_events:
                if event.bot_id:
                    return context.skip("Ignoring bot events")

                if event.subtype == "message_changed":
                    if event.message and event.message.get("bot_id"):
                        return context.skip("Ignoring bot message edits")
        return

    async def _post_handle(
        self,
        handle_type: str,
        handle_name: str,
        app: "Slackle",
        request: Request,
        response: Response,
        payload: SlackPayload,
        context: SlackleContext,
    ):
        """
        Post-handle the request after the handler has been called.
        This is where you can add custom logic after the handler is called.
        """
        await app.hooks.emit(
            app,
            "slack.post_handle",
            handle_type=handle_type,
            handle_name=handle_name,
            request=request,
            response=response,
            payload=payload,
            context=context,
        )

    async def _handle(
        self,
        handle_type: str,
        handle_name: str,
        app: "Slackle",
        request: Request,
        response: Response,
        payload: SlackPayload,
    ):
        """
        Handle the request and return a response.
        This is where you can add custom logic to handle the request.
        """

        handler = self._callback_registry.get(f"{handle_type}:{handle_name}")
        context = SlackleContext()
        if handler:
            params = inspect.signature(handler).parameters
            available_params = {
                "app": app,
                "payload": payload,
                "slack": app.slack,
                "request": request,
                "response": response,
                "context": context,
            }
            if handle_type == "events":
                available_params["event"] = payload.event
                available_params["event_type"] = payload.event.type
                available_params["user_id"] = payload.event.user
                available_params["channel_id"] = payload.event.channel

            if handle_type == "command":
                available_params["command"] = payload.command
                available_params["text"] = payload.text

            if handle_type == "interactivity":
                available_params["action"] = payload.actions[0]

            if hasattr(payload, "user_id"):
                available_params["user_id"] = payload.user_id
            if hasattr(payload, "user"):
                available_params["user_id"] = payload.user.get("id")

            if hasattr(payload, "channel_id"):
                available_params["channel_id"] = payload.channel_id
            if hasattr(payload, "channel"):
                available_params["channel_id"] = payload.channel.get("id")

            kwargs = {k: v for k, v in available_params.items() if k in params}
            await self._pre_handle(
                handle_type, handle_name, app, request, response, payload, context
            )

            if context.is_skipped:
                return
            try:
                await handler(**kwargs)
            except Exception as e:
                await app.hooks.emit(app, "slack.error", error=e, context=context)
                raise

            if context.is_skipped:
                return
            await self._post_handle(
                handle_type, handle_name, app, request, response, payload, context
            )
        else:
            await app.hooks.emit(app, "slack.unhandled", context=context)

    def _create_handler(
        self, handle_type: str, payload_type: Type[BaseModel], use_form: bool = False
    ) -> Callable[
        [Request, Response, SlackPayload, BackgroundTasks, "Slackle"],
        Awaitable[Response],
    ]:
        async def payload_handler(
            request: Request,
            response: Response,
            payload: (
                Annotated[payload_type, Depends(payload_type.as_form)] if use_form else payload_type
            ),
            background_tasks: BackgroundTasks,
            app: "Slackle" = Depends(get_app),
        ):
            if app.config.debug:
                print(payload)
            # if the payload is a SlackEventPayload and it has a challenge, return it
            if isinstance(payload, SlackEventPayload) and payload.challenge:
                return Response(content=payload.challenge, media_type="text/plain")
            background_tasks.add_task(
                self._handle,
                handle_type,
                self._extract_handle_name(handle_type, payload),
                app,
                request,
                response,
                payload,
            )
            return Response(status_code=status.HTTP_200_OK)

        return payload_handler

    def _register_routes(self):
        """
        Register the routes for the Slack payload handler.
        """
        for type_, model, *use_form in self._ROUTES:
            self.router.add_api_route(
                f"/{type_}",
                self._create_handler(type_, model, *(use_form or [False])),
                methods=["POST"],
            )

    def _extract_handle_name(self, handle_type: str, payload: SlackPayload) -> str:
        match handle_type:
            case "events":
                return payload.event.type
            case "command":
                return payload.command
            case "interactivity":
                if payload.actions and len(payload.actions) > 0:
                    return payload.actions[0].get("action_id", "unknown_action")
                return "unknown_action"
            case _:
                raise ValueError("Unsupported handle_type")

    def include_callback(self, callback: SlackCallback) -> None:
        """
        Include a callback registry into the current handler.
        """
        self._callback_registry.update_from(callback)
