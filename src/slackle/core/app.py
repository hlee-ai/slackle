"""
Slackle App
"""
from collections import defaultdict
from typing import Dict, List, Optional
from .command import SlackCommand
from .formatter import Formatter


class Slackle:
    def __init__(self):
        self.command_registry = SlackCommand()
        self.formatter_registry = Formatter()
        self.command_groups: Dict[str, List[str]] = defaultdict(list)

    def include_command(
            self,
            command_registry: SlackCommand,
            group: Optional[str] = None,
            override_group: bool = False
    ):
        for meta in command_registry.all():
            if group is not None and override_group:
                meta.group = group
            self.command_registry.register_meta(meta)
            self.command_groups[meta.group].append(meta.command)

    def include_formatter(self, formatter: Formatter):
        self.formatter_registry.update_from(formatter)