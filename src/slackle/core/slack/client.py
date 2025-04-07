from typing import Any, Dict, Optional

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from slackle.types.response import SlackBlock, SlackMarkdown, SlackResponse


class SlackClient:
    def __init__(self, token: str):
        self.client = AsyncWebClient(token=token)

    def _normalize_response(
        self,
        message: str | SlackMarkdown | SlackBlock | SlackResponse,
        channel: Optional[str],
    ) -> SlackResponse:
        if isinstance(message, SlackResponse):
            return message

        text = message.text if isinstance(message, SlackMarkdown) else message
        text = text if isinstance(text, str) else None
        blocks = message.blocks if isinstance(message, SlackBlock) else None

        return SlackResponse(channel=channel, text=text, blocks=blocks)

    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        response = await self.client.users_info(user=user_id)
        return response.get("user", {})

    async def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        response = await self.client.channels_info(channel=channel_id)
        return response.get("channel", {})

    async def get_user_name(self, user_id: str) -> Optional[str]:
        user_info = await self.get_user_info(user_id)
        return (
            user_info.get("profile", {}).get("display_name") or user_info.get("real_name") or None
        )

    async def get_channel_name(self, channel_id: str) -> Optional[str]:
        channel_info = await self.get_channel_info(channel_id)
        return channel_info.get("name") or channel_info.get("display_name") or None

    async def send_message(
        self,
        message: str | SlackMarkdown | SlackBlock | SlackResponse,
        channel: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
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
