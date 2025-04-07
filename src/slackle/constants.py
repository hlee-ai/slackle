from enum import Enum


class SlackResponseType(Enum):
    EPHEMERAL = "ephemeral"
    IN_CHANNEL = "in_channel"


class SlackVerificationMode(str, Enum):
    TOKEN = "token"
    SIGNATURE = "signature"


__all__ = ["SlackResponseType", "SlackVerificationMode"]
