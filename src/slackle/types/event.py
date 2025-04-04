from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class SlackEvent(BaseModel):
    type: str
    event_ts: str
    user: Optional[str] = None
    channel: Optional[str] = None
    team: Optional[str] = None
    ts: Optional[str] = None
    item: Optional[Dict[str, Any]] = None
    bot_id: Optional[str] = None
    app_id: Optional[str] = None
    team_id: Optional[str] = None
    bot_profile: Optional[Dict[str, Any]] = None

class SlackPayload(BaseModel):
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


__all__ = [
    "SlackEvent",
    "SlackPayload",
]