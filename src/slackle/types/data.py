from dataclasses import dataclass
from typing import Type
from .base import BaseSlackCommand

@dataclass
class SlackCommandMeta:
    command: str
    handler: Type[BaseSlackCommand]
    description: str
    group: str
    visible: bool = True