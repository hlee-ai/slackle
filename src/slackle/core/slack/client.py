"""
Slack Web API Client

This module defines the `SlackClient` class, a wrapper around Slack's AsyncWebClient.
It provides higher-level methods for interacting with Slack, such as sending messages,
retrieving user or channel information, and formatting payloads consistently.

The client instance is passed into the callback handlers, allowing them to interact with Slack's API
directly. The client can also be injected into FastAPI routes for more complex interactions.

Example usage:
@app.on_command("/hello")
async def handle_hello(app, slack, text, user_id, channel_id):
    user_name = await slack.get_user_name(user_id)
    channel_name = await slack.get_channel_name(channel_id)
    await slack.send_message(
        f"Hello {user_name} from {channel_name}!",
        channel=channel_id
    )
"""

from typing import Any, Dict, Optional

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from slackle.types.response import SlackBlock, SlackMarkdown, SlackResponse


class SlackClient:
    """
    Slack Web API Client

    This class is a wrapper around Slack's AsyncWebClient.
    It provides methods for sending messages, retrieving user and channel information,
    and normalizing responses for consistent handling.

    Properties:
        - client: The underlying AsyncWebClient instance.

    """

    def __init__(self, token: str):
        self.client = AsyncWebClient(token=token)

    def _normalize_response(
        self,
        message: str | SlackMarkdown | SlackBlock | SlackResponse,
        channel: Optional[str],
    ) -> SlackResponse:
        """
        Normalize the response message to a SlackResponse object.
        """
        if isinstance(message, SlackResponse):
            return message

        text = message.text if isinstance(message, SlackMarkdown) else message
        text = text if isinstance(text, str) else None
        blocks = message.blocks if isinstance(message, SlackBlock) else None

        return SlackResponse(channel=channel, text=text, blocks=blocks)

    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user information from Slack using the user ID.

        Args:
            user_id (str): The ID of the user to retrieve information for.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing user information,
            or None if not found.
        """
        response = await self.client.users_info(user=user_id)
        return response.get("user", {})

    async def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve channel information from Slack using the channel ID.

        Args:
            channel_id (str): The ID of the channel to retrieve information for.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing channel information,
            or None if not found.
        """
        response = await self.client.channels_info(channel=channel_id)
        return response.get("channel", {})

    async def get_user_name(self, user_id: str) -> Optional[str]:
        """
        Retrieve the display name or real name of a user.

        Args:
            user_id (str): The ID of the user to retrieve the name for.

        Returns:
            Optional[str]: The display name or real name of the user, or None if not found.
        """
        user_info = await self.get_user_info(user_id)
        return (
            user_info.get("profile", {}).get("display_name") or user_info.get("real_name") or None
        )

    async def get_channel_name(self, channel_id: str) -> Optional[str]:
        """
        Retrieve the display name or name of a channel.

        Args:
            channel_id (str): The ID of the channel to retrieve the name for.

        Returns:
            Optional[str]: The display name or name of the channel, or None if not found.
        """
        channel_info = await self.get_channel_info(channel_id)
        return channel_info.get("name") or channel_info.get("display_name") or None

    async def send_message(
        self,
        message: str | SlackMarkdown | SlackBlock | SlackResponse,
        channel: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message to a Slack channel.

        Args:
            message (str | SlackMarkdown | SlackBlock | SlackResponse): The message to send.
            channel (Optional[str]): The ID of the channel to send the message to.

        Returns:
            Optional[Dict[str, Any]]: The response data from Slack, or None if an error occurred.
        """
        try:
            response = self._normalize_response(message, channel)

            if not channel:
                raise ValueError("Channel is required")

            if not response.text and not response.blocks:
                raise ValueError("Either text or blocks must be provided")

            if response.blocks and isinstance(response.blocks, SlackBlock):
                response.blocks = response.blocks.blocks

            if not response.text and len(response.blocks) > 0:
                response.text = str(response.blocks)

            response = await self.client.chat_postMessage(
                channel=channel,
                text=response.text,
                blocks=response.blocks,
                attachments=response.attachments,
                response_type=response.response_type,
                thread_ts=response.thread_ts,
                reply_broadcast=response.reply_broadcast,
                icon_emoji=response.icon_emoji,
                icon_url=response.icon_url,
                link_names=response.link_names,
                mrkdwn=response.mrkdwn,
                parse=response.parse,
                unfurl_links=response.unfurl_links,
                unfurl_media=response.unfurl_media,
                username=response.username,
                metadata=response.metadata,
                as_user=response.as_user,
            )
            return response.data
        except SlackApiError as e:
            # TODO: if logging is enabled, log the error
            print(f"[SlackClient] Error sending message: {e}")
            return None

    # TODO: Add more methods like send_block, update_message, delete_message, open_modal, etc.
    async def send_ephemeral(
        self,
        channel: str,
        user: str,
        message: str | SlackMarkdown | SlackBlock | SlackResponse,
    ): ...

    async def update_message(
        self,
        channel: str,
        ts: str,
        message: str | SlackMarkdown | SlackBlock | SlackResponse,
    ): ...

    async def delete_message(
        self,
        channel: str,
        ts: str,
        message: str | SlackMarkdown | SlackBlock | SlackResponse,
    ): ...

    async def open_modal(self, trigger_id: str, view: dict): ...


__all__ = ["SlackClient"]
