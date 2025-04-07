from dataclasses import dataclass
from typing import Optional

from slackle.constants import SlackVerificationMode


@dataclass
class SlackleConfig:
    app_token: str = ""
    app_user_id: str = ""
    verification_mode: SlackVerificationMode = SlackVerificationMode.TOKEN
    verification_token: str = ""
    signing_secret: str = ""

    default_channel: Optional[str] = None

    enable_slack_blocks: bool = True
    enable_backslash_commands: bool = True

    ignore_bot_events: bool = True
    ignore_retry_events: bool = False

    # for development purposes only
    debug: bool = False
    unsafe_turnoff_token_verification: bool = False
