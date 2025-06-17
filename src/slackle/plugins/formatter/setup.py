from slackle.core.app import Slackle
from slackle.core.plugin import SlacklePlugin

from .formatter import Formatter


class FormatterPlugin(SlacklePlugin):
    def setup(self, app: Slackle):
        formatter = Formatter()

        def include_formatter(formatter: Formatter, override: bool = False):
            if override or not hasattr(self, "formatter"):
                self.formatter = formatter
            else:
                self.formatter.update_from(formatter)

        app.register_plugin_attribute("formatter", formatter)
        app.register_plugin_method("include_formatter", include_formatter, override=True)
