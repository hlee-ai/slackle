import inspect

from fastapi import APIRouter, Request, BackgroundTasks, Depends, Response, status
from fastapi.responses import JSONResponse

from slackle.core.slack.callback import SlackCallback
from slackle.types.event import SlackPayload
from slackle.dependencies import get_app
from slackle.types.context import SlackleContext
from typing import Callable, Awaitable, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from slackle.core.app import Slackle

class SlackPayloadHandler:
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
            context: SlackleContext
    ):
        """
        Pre-handle the request before passing it to the handler.
        This is where you can add custom logic before the handler is called.
        """

        if payload.event.bot_id and app.config.ignore_bot_events:
            context.skip("Ignoring bot events")
            return

        if request.headers.get("X-Slack-Retry-Num") and app.config.ignore_retry_events:
            context.skip("Ignoring retry events")
            return

        if handle_type == "events":
            event = payload.event
            if event.user == app.config.app_user_id:
                context.skip()
                return

        await app.hooks.emit(
            app,
            "slack.pre_handle",
            handle_type=handle_type,
            handle_name=handle_name,
            request=request,
            response=response,
            payload=payload,
            context=context
        )
        return

    async def _post_handle(
            self,
            handle_type: str,
            handle_name: str,
            app: "Slackle",
            request: Request,
            response: Response,
            payload: SlackPayload,
            context: SlackleContext
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
            context=context
        )

    async def _handle(
            self,
            handle_type: str,
            handle_name: str,
            app: "Slackle",
            request: Request,
            response: Response,
            payload: SlackPayload
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
            if handle_type == "action":
                available_params["action"] = payload.actions[0]
            kwargs = {k: v for k, v in available_params.items() if k in params}
            await self._pre_handle(handle_type, handle_name, app, request, response, payload, context)

            if context.is_skipped:
                return
            try:
                await handler(**kwargs)
            except Exception as e:
                await app.hooks.emit(app, "slack.error", error=e, context=context)
                raise

            if context.is_skipped:
                return
            await self._post_handle(handle_type, handle_name, app, request, response, payload, context)
        else:
            await app.hooks.emit(app, "slack.unhandled", context=context)

    def _create_handler(
            self,
            handle_type: str,
            handle_name: str
    ) -> Callable[[Request, Response, SlackPayload, BackgroundTasks, "Slackle"], Awaitable[JSONResponse]]:
        async def payload_handler(
                request: Request,
                response: Response,
                payload: SlackPayload,
                background_tasks: BackgroundTasks,
                app: "Slackle" = Depends(get_app),
        ):

            background_tasks.add_task(
                self._handle,
                handle_type,
                self._extract_handle_name(handle_type, payload),
                app,
                request,
                response,
                payload
            )
            return JSONResponse(content={"ok": True}, status_code=status.HTTP_200_OK)
        return payload_handler

    def _register_routes(self):
        """
        Register the routes for the Slack payload handler.
        """
        self.router.add_api_route(
            "/events",
            self._create_handler("events", "event"),
            methods=["POST"]
        )
        self.router.add_api_route(
            "/command",
            self._create_handler("command", "command"),
            methods=["POST"]
        )
        self.router.add_api_route(
            "/interactivity",
            self._create_handler("interactivity", "action"),
            methods=["POST"]
        )

    def _extract_handle_name(self, handle_type: str, payload: SlackPayload) -> str:
        match handle_type:
            case "events":
                return payload.event.type
            case "command":
                return payload.command  # e.g., "/hello"
            case "action":
                return payload.actions[0].action_id  # or use callback_id
            case _:
                raise ValueError("Unsupported handle_type")

    def include_callback(self, callback: SlackCallback) -> None:
        """
        Include a callback registry into the current handler.
        """
        self._callback_registry.update_from(callback)