import pytest

from slackle import Slackle, SlackleConfig
from slackle.utils.slack import get_user_mention


@pytest.fixture
def mock_config():
    return SlackleConfig(app_token="xapp-test", verification_token="verif-test")


@pytest.fixture
def app(mock_config):
    return Slackle(config=mock_config)


def test_slackle_initializes(app):
    assert isinstance(app, Slackle)


def test_register_event_handler(app):
    @app.on_event("message")
    async def message_handler(slack, user_id, channel_id):
        mention = get_user_mention(user_id)
        await slack.send_message(
            channel=channel_id,
            message=f"Hello {mention}!",
        )

    handler = app.callback.events.get("message")
    assert handler is not None
    assert handler.__name__ == "message_handler"


def test_register_command_handler(app):
    @app.on_command("/say")
    async def command_handler(slack, text, user_id, channel_id):
        name = await slack.get_user_name(user_id)
        await slack.send_message(
            channel=channel_id,
            message=f"{name} said: {text}",
        )

    handler = app.callback.commands.get("/say")
    assert handler is not None
    assert handler.__name__ == "command_handler"


def test_get_user_mention():
    user_id = "U12345"
    assert get_user_mention(user_id) == "<@U12345>"
