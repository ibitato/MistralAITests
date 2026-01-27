"""
Test cases for Mistral AI client.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.mistral_client import MistralAIClient
from src.utils import format_chat_message, truncate_text, validate_api_key


class TestMistralAIClient:
    """Test cases for MistralAIClient class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Mistral client."""
        with patch("src.mistral_client.Mistral") as mock:
            yield mock

    def test_initialization_with_api_key(self, mock_client):
        """Test client initialization with API key."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        client = MistralAIClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.model == "mistral-tiny"
        mock_client.assert_called_once_with(api_key="test_key")

    def test_initialization_without_api_key(self, mock_client):
        """Test client initialization without API key (uses env)."""
        import os

        with patch.dict(os.environ, {"MISTRAL_AI_API_KEY": "env_key"}):
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            client = MistralAIClient()
            assert client.api_key == "env_key"
            mock_client.assert_called_once_with(api_key="env_key")

    def test_chat_completion(self, mock_client):
        """Test chat completion method."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Hello, World!"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_instance.chat.complete.return_value = mock_response

        client = MistralAIClient(api_key="test_key")
        messages = [{"role": "user", "content": "Hello"}]

        result = client.chat_completion(messages)
        assert result == "Hello, World!"
        mock_instance.chat.complete.assert_called_once()


class TestUtils:
    """Test cases for utility functions."""

    def test_validate_api_key_valid(self):
        """Test API key validation with valid key."""
        assert validate_api_key("GNuBhN0w2K727QpgctBi24Hb1pNB4h0c")

    def test_validate_api_key_empty(self):
        """Test API key validation with empty key."""
        assert not validate_api_key("")

    def test_validate_api_key_short(self):
        """Test API key validation with short key."""
        assert not validate_api_key("short")

    def test_format_chat_message_valid(self):
        """Test chat message formatting with valid role."""
        from mistralai.models import UserMessage

        message = format_chat_message("user", "Hello")
        assert isinstance(message, UserMessage)
        assert message.role == "user"
        assert message.content == "Hello"

    def test_format_chat_message_invalid_role(self):
        """Test chat message formatting with invalid role."""
        with pytest.raises(ValueError):
            format_chat_message("invalid", "Hello")

    def test_truncate_text_no_truncation(self):
        """Test text truncation when no truncation needed."""
        assert truncate_text("Short text", 100) == "Short text"

    def test_truncate_text_with_truncation(self):
        """Test text truncation when truncation needed."""
        result = truncate_text(
            "This is a very long text that needs to be truncated", 20
        )
        assert result == "This is a very lo..."
        assert len(result) == 20
