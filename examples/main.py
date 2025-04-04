from time import sleep
from datetime import datetime

from slackle.config import SlackleConfig
from slackle.core.app import Slackle
from slackle.core.slack.client import SlackClient
from slackle.plugins.formatter import FormatterPlugin
from slackle.plugins.formatter.types import BaseFormatter, P
from slackle.types.response import SlackResponse, SlackMarkdown
import dotenv
import os

dotenv.load_dotenv()

config = SlackleConfig(
    app_token=os.getenv("APP_TOKEN"),
    verification_token=os.getenv("VERIFICATION_TOKEN"),
    # ignore_retry_events=True,
    debug=True,
)

slackle_app = Slackle(config=config)

slackle_app.add_plugin(FormatterPlugin)

class SampleData:
    name : str

@slackle_app.formatter.register(SampleData)
class SampleFormatter(BaseFormatter):
    def default_params(cls):
        return {}

    def to_slack_markdown(self) -> SlackMarkdown:
        return SlackMarkdown(text=f"Hello, {self.data.name}!")


@slackle_app.callback.event("app_mention")
async def on_mention(slack: SlackClient, user_id: str, channel_id: str):
    return await slack.send_message(SlackResponse(text=f"Hello, <@{user_id}>, I am Slackle!"), channel_id)

@slackle_app.callback.event("message")
async def on_message(app, payload, channel_id: str):
    user = payload.event.user
    return await app.slack.send_message(SlackResponse(text=f"Hello, <@{user}>, that is really a nice message!"), channel_id)