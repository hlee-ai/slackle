from typing import Optional

from slackle.core.app import Slackle
from slackle.core.plugin import SlacklePlugin

from .command import SlackCommand


class CommandPlugin(SlacklePlugin):
    def setup(self, app: Slackle):
        command = SlackCommand()

        def include_command(
            self,
            command_registry: SlackCommand,
            group: Optional[str] = None,
            override_group: bool = False,
        ):
            for meta in command_registry.all():
                if group is not None and override_group:
                    meta.group = group
                self.command.register_meta(meta)

        app.register_plugin_attribute("command", command)
        app.register_plugin_method("include_command", include_command, override=True)


__all__ = ["CommandPlugin"]
