<p align="center">
  <a href="https://slackle.dev">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://slackle.dev/static/logo-light.png">
      <source media="(prefers-color-scheme: light)" srcset="https://slackle.dev/static/logo-dark.png">
      <img alt="Slackle" src="https://slackle.dev/static/logo-dark.png" width="500">
    </picture>
  </a>
</p>

<p align="center">
  <a href="https://slackle.dev"><img src="https://img.shields.io/badge/✨_Slackle-Magic_Framework-purple" alt="Slackle Framework"/></a>
  <a href="https://pypi.org/project/slackle/"><img src="https://img.shields.io/pypi/v/slackle?label=PyPI" alt="PyPI Version"/></a>
  <a href="https://slack.dev"><img src="https://img.shields.io/badge/built_with-Slack_SDK_+_FastAPI-4A154B?logo=slack" alt="Slack + FastAPI"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-yellow?logo=python" alt="Python Version"/></a>
</p>

---

## ✨ Slackle up your Slack!

[**Slackle**](https://slackle.dev) is a lightweight and magical framework for building Slack apps effortlessly.

[→ Visit the Official Website](https://slackle.dev)

---

## 🚀 Features

- ⚡️ **Slash command routing** — Handle `/your-command`, `/like`, `/magic`
- 💬 **Event handling** — `@app_mention`, `message`, `reaction_added`, etc.
- 🎨 **Slack formatting** — Clean markdown and block formatting made easy
- 🧩 **Plugin system** — Extend functionality with decorators and custom plugins
- ⚙️ **FastAPI + Slack SDK** — Built on proven tools, superfast and flexible

---

## 📦 Installation

```bash
pip install slackle
```

---

## 🧑‍💻 Getting Started

```python
import os

from slackle import Slackle, SlackleConfig
from slackle.utils.slack import get_user_mention

# Set up slackle configuration
config = SlackleConfig(
    app_token=os.getenv("APP_TOKEN"),
    verification_token=os.getenv("VERIFICATION_TOKEN")
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
```

---

> 📁 See [examples/](examples) for more code samples.

## 🤝 Contribution

We welcome contributions!
Check out the [Contributing Guide](CONTRIBUTING.md) to get started.

---

## 🪪 License

MIT License. See the [LICENSE](LICENSE) file for details.

