"""
Test cases for Mistral AI client.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.determinism_controller import DeterminismController
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

    def test_chat_completion_with_determinism_level(self, mock_client):
        """Test chat completion with different determinism levels."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Deterministic response"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_instance.chat.complete.return_value = mock_response

        client = MistralAIClient(api_key="test_key")
        messages = [{"role": "user", "content": "Test"}]

        # Test level 1 (most exact)
        result = client.chat_completion(messages, determinism_level=1)
        assert result == "Deterministic response"

        # Test level 5 (most creative)
        result = client.chat_completion(messages, determinism_level=5)
        assert result == "Deterministic response"

    def test_determinism_controller(self):
        """Test determinism controller levels."""
        # Test level 1 (most exact) - Note: top_p=1.0 for Mistral API compatibility with greedy sampling
        controller = DeterminismController(level=1)
        params = controller.get_parameters()
        assert params["temperature"] == 0.0
        assert (
            params["top_p"] == 1.0
        )  # Mistral API requires top_p=1 when using greedy sampling

        # Test level 3 (balanced - default)
        controller = DeterminismController(level=3)
        params = controller.get_parameters()
        assert params["temperature"] == 0.3
        assert params["top_p"] == 0.5

        # Test level 5 (most creative)
        controller = DeterminismController(level=5)
        params = controller.get_parameters()
        assert params["temperature"] == 0.7
        assert params["top_p"] == 0.9

    def test_determinism_controller_invalid_level(self):
        """Test determinism controller with invalid level."""
        with pytest.raises(ValueError):
            DeterminismController(level=0)

        with pytest.raises(ValueError):
            DeterminismController(level=6)

    def test_temperature_override_with_greedy_sampling(self, mock_client):
        """Test temperature override logic with greedy sampling (temperature=0.0)."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Exact response"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_instance.chat.complete.return_value = mock_response

        client = MistralAIClient(api_key="test_key")
        messages = [{"role": "user", "content": "Test"}]

        # Test temperature=0.0 override (should set top_p=1.0 for Mistral API compatibility)
        result = client.chat_completion(messages, temperature=0.0)
        assert result == "Exact response"

        # Verify that the call included top_p=1.0 when temperature=0.0
        call_args = mock_instance.chat.complete.call_args
        assert call_args[1]["temperature"] == 0.0
        assert call_args[1]["top_p"] == 1.0

    def test_dynamic_level_switching(self, mock_client):
        """Test dynamic determinism level switching during runtime."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Dynamic response"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_instance.chat.complete.return_value = mock_response

        client = MistralAIClient(api_key="test_key", determinism_level=3)
        messages = [{"role": "user", "content": "Test"}]

        # Test initial level (3)
        result = client.chat_completion(messages)
        assert result == "Dynamic response"

        # Verify initial level parameters
        call_args = mock_instance.chat.complete.call_args
        assert call_args[1]["temperature"] == 0.3
        assert call_args[1]["top_p"] == 0.5

        # Test switching to level 2
        result = client.chat_completion(messages, determinism_level=2)
        assert result == "Dynamic response"

        # Verify level 2 parameters
        call_args = mock_instance.chat.complete.call_args
        assert call_args[1]["temperature"] == 0.1
        assert call_args[1]["top_p"] == 0.2

    def test_chat_completion_stream(self, mock_client):
        """Test streaming chat completion method."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock streaming response
        mock_chunk1 = MagicMock()
        mock_delta1 = MagicMock()
        mock_delta1.content = "Hello"
        mock_choice1 = MagicMock()
        mock_choice1.delta = mock_delta1
        mock_chunk1.choices = [mock_choice1]

        mock_chunk2 = MagicMock()
        mock_delta2 = MagicMock()
        mock_delta2.content = " World"
        mock_choice2 = MagicMock()
        mock_choice2.delta = mock_delta2
        mock_chunk2.choices = [mock_choice2]

        mock_chunk3 = MagicMock()
        mock_delta3 = MagicMock()
        mock_delta3.content = "!"
        mock_choice3 = MagicMock()
        mock_choice3.delta = mock_delta3
        mock_chunk3.choices = [mock_choice3]

        mock_instance.chat.stream.return_value = [mock_chunk1, mock_chunk2, mock_chunk3]

        client = MistralAIClient(api_key="test_key")
        messages = [{"role": "user", "content": "Hello"}]

        # Test streaming
        chunks = list(client.chat_completion_stream(messages))
        assert chunks == ["Hello", " World", "!"]

        # Verify streaming was called with correct parameters
        mock_instance.chat.stream.assert_called_once()

    def test_chat_completion_with_metrics(self, mock_client):
        """Test chat completion with metrics method."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response with usage data
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_response.usage = mock_usage

        mock_instance.chat.complete.return_value = mock_response

        client = MistralAIClient(api_key="test_key")
        messages = [{"role": "user", "content": "Test"}]

        # Test with metrics
        result = client.chat_completion_with_metrics(messages)

        # Verify result structure
        assert "content" in result
        assert "duration" in result
        assert "tokens" in result
        assert "model" in result
        assert "level" in result
        assert "parameters" in result
        assert "metrics" in result

        assert result["content"] == "Test response"
        assert result["tokens"]["total"] == 30
        assert result["tokens"]["prompt"] == 10
        assert result["tokens"]["completion"] == 20
        assert result["model"] == "mistral-tiny"
        assert result["level"] == 3

    def test_error_handling_empty_messages(self):
        """Test error handling for empty messages."""
        client = MistralAIClient(api_key="test_key")

        # Test empty messages list
        with pytest.raises(ValueError, match="Messages list cannot be empty"):
            client.chat_completion([])

        with pytest.raises(ValueError, match="Messages list cannot be empty"):
            list(client.chat_completion_stream([]))

        with pytest.raises(ValueError, match="Messages list cannot be empty"):
            client.chat_completion_with_metrics([])

    def test_error_handling_api_failures(self, mock_client):
        """Test error handling for API failures."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock API exception
        mock_instance.chat.complete.side_effect = Exception("API Error")

        client = MistralAIClient(api_key="test_key")
        messages = [{"role": "user", "content": "Test"}]

        # Test error handling in regular completion
        with pytest.raises(RuntimeError, match="Failed to get chat completion"):
            client.chat_completion(messages)

        # Test error handling in streaming
        mock_instance.chat.stream.side_effect = Exception("Streaming Error")
        with pytest.raises(RuntimeError, match="Streaming failed"):
            list(client.chat_completion_stream(messages))

        # Test error handling in metrics
        mock_instance.chat.complete.side_effect = Exception("Metrics Error")
        with pytest.raises(
            RuntimeError, match="Failed to get chat completion with metrics"
        ):
            client.chat_completion_with_metrics(messages)


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
