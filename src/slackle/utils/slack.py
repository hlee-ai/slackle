import re


def get_user_mention(user_id: str):
    """
    Get the mention string for a user.
    :param user_id: Slack user ID
    :return: Mention string
    """
    return f"<@{user_id}>"


def get_channel_mention(channel_id: str):
    """
    Get the mention string for a channel.
    """
    return f"<#{channel_id}>"


def get_user_id_from_mention(mention: str) -> str:
    """
    Extract user ID from a mention string.
    """
    if mention.startswith("<@") and mention.endswith(">"):
        return mention[2:-1]
    return mention


def get_channel_id_from_mention(mention: str) -> str:
    """
    Extract channel ID from a mention string.
    """
    if mention.startswith("<#") and mention.endswith(">"):
        return mention[2:-1]
    return mention


def get_mentions_from_text(text: str) -> list[str]:
    """
    Extract mentions from a text string.
    :param text: Text containing mentions
    :return: List of user IDs
    """
    return re.findall(r"<@([A-Z0-9]+)>", text)
