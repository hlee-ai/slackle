import os
from dataclasses import dataclass

from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from slackle.config import SlackleConfig
from slackle.core.app import Slackle
from slackle.core.slack.client import SlackClient
from slackle.plugins.formatter import FormatterPlugin
from slackle.plugins.formatter.types import BaseFormatter
from slackle.types.payload import SlackEvent
from slackle.types.response import SlackBlock, SlackMarkdown, SlackResponse
from slackle.utils.slack import get_channel_mention, get_user_mention

config = SlackleConfig(
    app_token=os.getenv("APP_TOKEN"),
    verification_token=os.getenv("VERIFICATION_TOKEN"),
    debug=True,
)

slackle = Slackle(config=config)
slackle.add_plugin(FormatterPlugin)


@slackle.exception_handler(RequestValidationError)
async def exception_handler(request: Request, exc: RequestValidationError):
    import json

    print(json.dumps(await request.json(), indent=2))
    print("Exception occurred:", exc)
    import traceback

    traceback.print_exc()
    return JSONResponse(status_code=500, content={"ok": False, "error": str(exc)})


@dataclass
class UserData:
    name: str
    user_id: str


@dataclass
class GreetingFormatterParams:
    emoji: str = ""


@slackle.formatter.register(UserData)
class GreetingFormatter(BaseFormatter):
    data_type = UserData

    @classmethod
    def default_params(cls):
        return GreetingFormatterParams()

    def to_slack_markdown(self) -> SlackMarkdown:
        return SlackMarkdown(
            text=f"{get_user_mention(self.data.user_id)} "
            f"{self.parameters.emoji} Hello, {self.data.name} "
            f"Welcome to Slackle! "
        )


@slackle.on_event("app_mention")
async def on_mention(app: Slackle, slack: SlackClient, user_id: str, channel_id: str):
    name = await slack.get_user_name(user_id) or "unknown"
    print(await slack.get_user_info(user_id))
    data = UserData(name=name, user_id=user_id)
    parameter = GreetingFormatterParams(emoji=":wave:")
    formatter = app.formatter.get(UserData)(data, parameter)
    message = formatter.to_slack_markdown()
    return await slack.send_message(message, channel_id)


@slackle.on_event("message")
async def on_message(slack: SlackClient, event: SlackEvent, channel_id: str, request: Request):
    user = event.user
    return await slack.send_message(
        SlackBlock(
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hello {get_user_mention(user)}! "
                        f"You sent a message in {get_channel_mention(channel_id)}.",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "If you are interested in this project, "
                        "feel free to check out the repository:",
                    },
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Github"},
                        "url": "https://github.com/hlee-ai/slackle",
                    },
                },
            ]
        ),
        channel_id,
    )


@slackle.on_command("/hello")
async def hello_command(slack: SlackClient, text: str, channel_id: str):
    if not text:
        return slack.send_message(SlackMarkdown(text="Please provide a name."), channel_id)
    return slack.send_message(
        SlackResponse(
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"Hello, {text}"},
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Click Me",
                        },
                        "value": "click_me_123",
                        "action_id": "button-action",
                    },
                }
            ]
        ),
        channel_id,
    )


@slackle.on_action("button-action")
async def button_action(slack: SlackClient, user_id: str, channel_id: str):
    return await slack.send_message(
        SlackMarkdown(text=f"Button clicked by {get_user_mention(user_id)}"), channel_id
    )
