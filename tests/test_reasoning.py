"""
Test cases for Mistral AI reasoning functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.mistral_client import MistralAIClient


class TestReasoning:
    """Test cases for reasoning functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Mistral client."""
        with patch("src.mistral_client.Mistral") as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            yield mock

    @pytest.fixture
    def client(self, mock_client):
        """Create a test client."""
        return MistralAIClient(api_key="test_key", model="mistral-tiny")

    def test_chat_completion_with_reasoning_enabled(self, client, mock_client):
        """Test chat completion with reasoning enabled."""
        # Setup mock response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Thinking step by step... Final answer: Paris"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.return_value.chat.complete.return_value = mock_response

        # Test messages without system message
        messages = [
            {"role": "user", "content": "What is the capital of France?"}
        ]

        result = client.chat_completion(messages, reasoning=True)

        # Verify reasoning instruction was added
        call_args = mock_client.return_value.chat.complete.call_args
        actual_messages = call_args[1]["messages"]
        
        # Should have added system message with reasoning instruction
        assert len(actual_messages) == 2
        assert actual_messages[0]["role"] == "system"
        assert "thinks step by step" in actual_messages[0]["content"]
        assert "Show your reasoning process" in actual_messages[0]["content"]
        
        # Verify result contains reasoning output
        assert "Thinking step by step" in result
        assert "Paris" in result

    def test_chat_completion_with_reasoning_and_existing_system(self, client, mock_client):
        """Test reasoning with existing system message."""
        # Setup mock response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Reasoning: Step 1, Step 2. Answer: 42"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.return_value.chat.complete.return_value = mock_response

        # Test messages with existing system message
        messages = [
            {"role": "system", "content": "You are a math assistant."},
            {"role": "user", "content": "What is the meaning of life?"}
        ]

        result = client.chat_completion(messages, reasoning=True)

        # Verify reasoning instruction was appended to existing system message
        call_args = mock_client.return_value.chat.complete.call_args
        actual_messages = call_args[1]["messages"]
        
        # Should still have 2 messages, but system message should be modified
        assert len(actual_messages) == 2
        assert actual_messages[0]["role"] == "system"
        assert "You are a math assistant" in actual_messages[0]["content"]
        assert "Show your reasoning process" in actual_messages[0]["content"]
        
        # Verify result
        assert "Reasoning:" in result

    def test_chat_completion_with_reasoning_disabled(self, client, mock_client):
        """Test chat completion with reasoning disabled (default)."""
        # Setup mock response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Paris"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.return_value.chat.complete.return_value = mock_response

        messages = [
            {"role": "user", "content": "What is the capital of France?"}
        ]

        result = client.chat_completion(messages, reasoning=False)

        # Verify no reasoning instruction was added
        call_args = mock_client.return_value.chat.complete.call_args
        actual_messages = call_args[1]["messages"]
        
        # Should have original messages only
        assert len(actual_messages) == 1
        assert actual_messages[0]["role"] == "user"
        
        # Verify result is simple answer
        assert result == "Paris"

    def test_chat_completion_with_metrics_and_reasoning(self, client, mock_client):
        """Test chat completion with metrics and reasoning enabled."""
        # Setup mock response with usage data
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Thinking... Final answer: Madrid"
        mock_choice.message = mock_message
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        mock_client.return_value.chat.complete.return_value = mock_response

        messages = [
            {"role": "user", "content": "What is the capital of Spain?"}
        ]

        result = client.chat_completion_with_metrics(messages, reasoning=True)

        # Verify result structure
        assert "content" in result
        assert "duration" in result
        assert "tokens" in result
        assert "reasoning_enabled" in result
        
        # Verify reasoning was enabled
        assert result["reasoning_enabled"] is True
        
        # Verify content contains reasoning
        assert "Thinking" in result["content"]
        assert "Madrid" in result["content"]
        
        # Verify token metrics
        assert result["tokens"]["total"] == 30
        assert result["tokens"]["prompt"] == 10
        assert result["tokens"]["completion"] == 20

    def test_reasoning_with_different_determinism_levels(self, client, mock_client):
        """Test reasoning works with different determinism levels."""
        # Setup mock response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Reasoning at level 5: Creative answer!"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.return_value.chat.complete.return_value = mock_response

        messages = [
            {"role": "user", "content": "Be creative!"}
        ]

        # Test with level 5 (creative)
        result = client.chat_completion(messages, determinism_level=5, reasoning=True)

        # Verify determinism level was used
        call_args = mock_client.return_value.chat.complete.call_args
        params = call_args[1]
        
        # Should have creative parameters
        assert params["temperature"] >= 0.7  # Creative level should have high temperature
        
        # Verify reasoning instruction was added
        actual_messages = call_args[1]["messages"]
        assert "Show your reasoning process" in actual_messages[0]["content"]
        
        # Verify result
        assert "Reasoning at level 5" in result

    def test_reasoning_modifies_messages_for_api_call(self, client, mock_client):
        """Test that reasoning modifies messages for API call but preserves original structure."""
        # Setup mock response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Reasoned response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.return_value.chat.complete.return_value = mock_response

        # Original messages
        original_messages = [
            {"role": "system", "content": "Original system message."},
            {"role": "user", "content": "Original user question?"}
        ]
        
        # Call with reasoning
        result = client.chat_completion(original_messages, reasoning=True)

        # Verify API was called with modified messages
        call_args = mock_client.return_value.chat.complete.call_args
        actual_messages = call_args[1]["messages"]
        
        # Should still have 2 messages
        assert len(actual_messages) == 2
        assert actual_messages[0]["role"] == "system"
        assert actual_messages[1]["role"] == "user"
        
        # System message should have reasoning instruction added
        assert "Original system message" in actual_messages[0]["content"]
        assert "Show your reasoning process" in actual_messages[0]["content"]
        assert actual_messages[0]["content"] != "Original system message."
        
        # User message should be unchanged
        assert actual_messages[1]["content"] == "Original user question?"
        
        # Verify result
        assert result == "Reasoned response"
