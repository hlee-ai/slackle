import json
from typing import Annotated, Any, Dict, List, Optional

from fastapi import Form
from pydantic import BaseModel


class SlackEvent(BaseModel):
    type: str
    subtype: Optional[str] = None
    event_ts: str
    user: Optional[str] = None
    channel: Optional[str] = None
    team: Optional[str] = None
    ts: Optional[str] = None
    item: Optional[Dict[str, Any]] = None
    message: Optional[Dict[str, Any]] = None
    bot_id: Optional[str] = None
    app_id: Optional[str] = None
    team_id: Optional[str] = None
    bot_profile: Optional[Dict[str, Any]] = None


class SlackEventPayload(BaseModel):
    token: str
    team_id: Optional[str] = None
    api_app_id: Optional[str] = None
    event: Optional[SlackEvent] = None
    command: Optional[str] = None
    actions: Optional[List[Dict[str, Any]]] = None
    type: str
    event_id: Optional[str] = None
    event_time: Optional[int] = None
    authorizations: Optional[List[Dict[str, Any]]] = None
    is_ext_shared_channel: Optional[bool] = None
    event_context: Optional[str] = None
    challenge: Optional[str] = None


class SlackInteractionPayload(BaseModel):
    type: str
    token: str
    team: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None
    api_app_id: Optional[str] = None
    channel: Optional[Dict[str, Any]] = None
    response_url: str
    trigger_id: str
    view: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def as_form(
        cls,
        payload: Annotated[str, Form(...)],
    ):
        payload_dict = json.loads(payload)
        return cls(**payload_dict)


class SlackCommandPayload(BaseModel):
    token: str
    team_id: Optional[str] = None
    team_domain: Optional[str] = None
    enterprise_id: Optional[str] = None
    enterprise_name: Optional[str] = None
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    command: str
    text: str
    response_url: str
    trigger_id: Optional[str] = None
    api_app_id: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        token: str = Form(...),
        team_id: Optional[str] = Form(None),
        team_domain: Optional[str] = Form(None),
        enterprise_id: Optional[str] = Form(None),
        enterprise_name: Optional[str] = Form(None),
        channel_id: Optional[str] = Form(None),
        channel_name: Optional[str] = Form(None),
        user_id: Optional[str] = Form(None),
        user_name: Optional[str] = Form(None),
        command: str = Form(...),
        text: str = Form(...),
        response_url: str = Form(...),
        trigger_id: Optional[str] = Form(None),
        api_app_id: Optional[str] = Form(None),
    ):
        return cls(
            token=token,
            team_id=team_id,
            team_domain=team_domain,
            enterprise_id=enterprise_id,
            enterprise_name=enterprise_name,
            channel_id=channel_id,
            channel_name=channel_name,
            user_id=user_id,
            user_name=user_name,
            command=command,
            text=text,
            response_url=response_url,
            trigger_id=trigger_id,
            api_app_id=api_app_id,
        )


SlackPayload = SlackEventPayload | SlackCommandPayload | SlackInteractionPayload

__all__ = [
    "SlackEvent",
    "SlackEventPayload",
    "SlackCommandPayload",
    "SlackPayload",
]
