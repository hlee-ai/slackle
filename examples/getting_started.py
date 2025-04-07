import os

from slackle import Slackle, SlackleConfig
from slackle.utils.slack import get_user_mention

# Set up slackle configuration
config = SlackleConfig(
    app_token=os.getenv("APP_TOKEN"), verification_token=os.getenv("VERIFICATION_TOKEN")
)

# Initialize slackle app
app = Slackle(config=config)


# Add handler for message events
@app.on_event("message")
async def say_hello(slack, user_id, channel_id):
    mention = get_user_mention(user_id)
    print("User ID:", user_id)
    await slack.send_message(
        channel=channel_id,
        message=f"Hello {mention}!",
    )


# Add handler for /say slash command
@app.on_command("/say")
async def say_something(slack, text, user_id, channel_id):
    name = await slack.get_user_name(user_id)
    await slack.send_message(
        channel=channel_id,
        message=f"{name} said: {text}",
    )
