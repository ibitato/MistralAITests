"""
Utility functions for Mistral AI project.
"""

import logging

from mistralai.models import AssistantMessage, SystemMessage, UserMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_api_key(api_key: str | None) -> bool:
    """Validate Mistral AI API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if API key appears valid, False otherwise
    """
    if not api_key:
        logger.error("API key is empty")
        return False

    if len(api_key) < 20:
        logger.error("API key is too short")
        return False

    if not api_key.startswith("GNu"):
        logger.warning("API key may not be valid Mistral AI format")
        # Still return True as this could be a custom key

    return True


def format_chat_message(
    role: str, content: str
) -> UserMessage | AssistantMessage | SystemMessage:
    """Format chat message for Mistral AI API.

    Args:
        role: Message role (user, assistant, system)
        content: Message content

    Returns:
        Formatted message object
    """
    if role == "user":
        return UserMessage(role="user", content=content)
    elif role == "assistant":
        return AssistantMessage(role="assistant", content=content)
    elif role == "system":
        return SystemMessage(role="system", content=content)
    else:
        raise ValueError(f"Invalid role: {role}")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."
