from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from slackle.constants import SlackResponseType


@dataclass
class SlackMarkdown:
    text: str


@dataclass
class SlackBlock:
    blocks: List[Dict[str, Any]]


@dataclass
class SlackResponse:
    channel: str = None
    text: Optional[Union[str, SlackMarkdown]] = None
    blocks: Optional[Union[SlackBlock, List[Dict[str, any]]]] = None
    attachments: Optional[List[Dict[str, any]]] = None

    response_type: Optional[SlackResponseType] = None
    thread_ts: Optional[str] = None
    reply_broadcast: Optional[bool] = None
    icon_emoji: Optional[str] = None
    icon_url: Optional[str] = None
    link_names: Optional[bool] = None
    mrkdwn: Optional[bool] = True
    parse: Optional[str] = None
    unfurl_links: Optional[bool] = None
    unfurl_media: Optional[bool] = None
    username: Optional[str] = None
    metadata: Optional[Dict[str, any]] = None
    as_user: Optional[bool] = None
