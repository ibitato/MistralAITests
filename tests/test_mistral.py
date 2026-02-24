"""
Test cases for Mistral AI client.
"""

import json
from unittest.mock import MagicMock, patch, mock_open

import pytest

from src.determinism_controller import DeterminismController
from src.mistral_client import MistralAIClient
from mistralai.models import Function, Tool, ToolCall

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


class TestToolCalling:
    """Test cases for tool calling functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Mistral client."""
        with patch("src.mistral_client.Mistral") as mock:
            yield mock

    @pytest.fixture
    def sample_tools(self):
        """Create sample tools for testing."""
        return [
            Tool(
                type="function",
                function=Function(
                    name="get_weather",
                    description="Get weather for a location",
                    parameters={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City and country"
                            }
                        },
                        "required": ["location"]
                    }
                )
            ),
            Tool(
                type="function",
                function=Function(
                    name="calculate",
                    description="Calculate mathematical expression",
                    parameters={
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Math expression"
                            }
                        },
                        "required": ["expression"]
                    }
                )
            )
        ]

    @pytest.fixture
    def sample_functions(self):
        """Create sample functions for testing."""
        def get_weather(location: str) -> dict:
            return {"location": location, "temperature": 22, "unit": "celsius"}

        def calculate(expression: str) -> dict:
            return {"expression": expression, "result": eval(expression)}

        return {
            "get_weather": get_weather,
            "calculate": calculate
        }

    def test_chat_completion_with_tools_basic(self, mock_client, sample_tools):
        """Test basic tool calling functionality."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response with tool calls
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = None  # No content when tool calls are made
        
        # Mock tool call
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.type = "function"
        mock_function = MagicMock()
        mock_function.name = "get_weather"
        mock_function.arguments = '{"location": "Paris, France"}'
        mock_tool_call.function = mock_function
        
        mock_message.tool_calls = [mock_tool_call]
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        # Mock usage
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 15
        mock_usage.completion_tokens = 25
        mock_response.usage = mock_usage
        
        mock_instance.chat.complete.return_value = mock_response

        client = MistralAIClient(api_key="test_key")
        messages = [{"role": "user", "content": "What's the weather in Paris?"}]

        result = client.chat_completion_with_tools(
            messages=messages,
            tools=sample_tools,
            temperature=0.3
        )

        # Verify result structure
        assert "content" in result
        assert "tool_calls" in result
        assert "duration" in result
        assert "tokens" in result
        assert "model" in result
        assert "level" in result
        assert "parameters" in result

        # Verify content is None (tool calls were made)
        assert result["content"] is None

        # Verify tool calls
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["id"] == "call_123"
        assert result["tool_calls"][0]["type"] == "function"
        assert result["tool_calls"][0]["function"]["name"] == "get_weather"

        # Verify token usage
        assert result["tokens"]["total"] == 40
        assert result["tokens"]["prompt"] == 15
        assert result["tokens"]["completion"] == 25

    def test_chat_completion_with_tools_validation(self, mock_client, sample_tools):
        """Test tool calling validation."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        client = MistralAIClient(api_key="test_key")

        # Test empty messages
        with pytest.raises(ValueError, match="Messages list cannot be empty"):
            client.chat_completion_with_tools([], sample_tools)

        # Test empty tools
        with pytest.raises(ValueError, match="Tools list cannot be empty"):
            client.chat_completion_with_tools(
                [{"role": "user", "content": "Test"}], []
            )

    def test_chat_completion_with_tools_no_tool_calls(self, mock_client, sample_tools):
        """Test tool calling when no tools are called."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response without tool calls
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "I don't need to use any tools for this."
        mock_message.tool_calls = None  # No tool calls
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        # Mock usage
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_response.usage = mock_usage
        
        mock_instance.chat.complete.return_value = mock_response

        client = MistralAIClient(api_key="test_key")
        messages = [{"role": "user", "content": "What's 2+2?"}]

        result = client.chat_completion_with_tools(
            messages=messages,
            tools=sample_tools,
            tool_choice="none"  # Force no tool calls
        )

        # Verify content is present
        assert result["content"] == "I don't need to use any tools for this."

        # Verify no tool calls
        assert result["tool_calls"] == []

    def test_execute_tool_calls_success(self, sample_tools, sample_functions):
        """Test successful tool execution."""
        client = MistralAIClient(api_key="test_key")

        # Sample tool call
        tool_call = {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "Paris, France"}'
            }
        }

        result = client.execute_tool_calls(
            tool_calls=[tool_call],
            available_functions=sample_functions
        )

        # Verify tool response
        assert len(result) == 1
        assert result[0]["tool_call_id"] == "call_123"
        assert result[0]["role"] == "tool"
        assert result[0]["name"] == "get_weather"

        # Verify function was executed
        content = json.loads(result[0]["content"])
        assert content["location"] == "Paris, France"
        assert content["temperature"] == 22

    def test_execute_tool_calls_error(self, sample_functions):
        """Test tool execution with error handling."""
        client = MistralAIClient(api_key="test_key")

        # Tool call for non-existent function
        tool_call = {
            "id": "call_error",
            "type": "function",
            "function": {
                "name": "non_existent_function",
                "arguments": '{"param": "value"}'
            }
        }

        result = client.execute_tool_calls(
            tool_calls=[tool_call],
            available_functions=sample_functions
        )

        # Verify error response
        assert len(result) == 1
        assert result[0]["tool_call_id"] == "call_error"
        assert result[0]["name"] == "non_existent_function"

        # Verify error content
        content = json.loads(result[0]["content"])
        assert "error" in content
        assert content["success"] is False

    def test_execute_tool_calls_validation(self, sample_functions):
        """Test tool execution validation."""
        client = MistralAIClient(api_key="test_key")

        # Test empty tool calls
        with pytest.raises(ValueError, match="Tool calls list cannot be empty"):
            client.execute_tool_calls([], sample_functions)

        # Test empty functions
        with pytest.raises(ValueError, match="Available functions dictionary cannot be empty"):
            client.execute_tool_calls(
                [{"id": "test", "function": {"name": "test", "arguments": "{}"}}],
                {}
            )

    def test_chat_completion_with_tool_execution_full_workflow(
        self, mock_client, sample_tools, sample_functions
    ):
        """Test full tool execution workflow."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # First call - model decides to use tool
        mock_response1 = MagicMock()
        mock_message1 = MagicMock()
        mock_message1.content = None
        
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.type = "function"
        mock_function = MagicMock()
        mock_function.name = "calculate"
        mock_function.arguments = '{"expression": "15 * 3"}'
        mock_tool_call.function = mock_function
        
        mock_message1.tool_calls = [mock_tool_call]
        mock_choice1 = MagicMock()
        mock_choice1.message = mock_message1
        mock_response1.choices = [mock_choice1]
        
        mock_usage1 = MagicMock()
        mock_usage1.prompt_tokens = 10
        mock_usage1.completion_tokens = 20
        mock_response1.usage = mock_usage1

        # Second call - model gets tool response and provides final answer
        mock_response2 = MagicMock()
        mock_message2 = MagicMock()
        mock_message2.content = "The result is 45."
        mock_message2.tool_calls = None
        mock_choice2 = MagicMock()
        mock_choice2.message = mock_message2
        mock_response2.choices = [mock_choice2]
        
        mock_usage2 = MagicMock()
        mock_usage2.prompt_tokens = 15
        mock_usage2.completion_tokens = 10
        mock_response2.usage = mock_usage2

        # Mock the sequence of calls - need 3 calls total
        # 1. First call with tool_choice="auto" -> returns tool call
        # 2. Second call with tool_choice="none" -> returns final answer
        mock_instance.chat.complete.side_effect = [mock_response1, mock_response2, mock_response2]

        client = MistralAIClient(api_key="test_key")
        messages = [{"role": "user", "content": "What's 15 * 3?"}]

        result = client.chat_completion_with_tool_execution(
            messages=messages,
            tools=sample_tools,
            available_functions=sample_functions,
            max_iterations=2
        )

        # Verify full workflow result
        assert "final_response" in result
        assert "all_messages" in result
        assert "tool_execution_history" in result
        assert "iterations" in result
        assert "tokens_used" in result
        assert "duration" in result

        # Verify final response
        assert result["final_response"] == "The result is 45."

        # Verify tool execution history
        assert len(result["tool_execution_history"]) == 1
        assert result["tool_execution_history"][0]["function"] == "calculate"
        assert result["tool_execution_history"][0]["success"] is True

        # Verify iterations
        assert result["iterations"] == 2

    def test_chat_completion_with_tool_execution_validation(
        self, mock_client, sample_tools, sample_functions
    ):
        """Test tool execution workflow validation."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        client = MistralAIClient(api_key="test_key")

        # Test empty messages
        with pytest.raises(ValueError, match="Messages list cannot be empty"):
            client.chat_completion_with_tool_execution(
                [], sample_tools, sample_functions
            )

        # Test empty tools
        with pytest.raises(ValueError, match="Tools list cannot be empty"):
            client.chat_completion_with_tool_execution(
                [{"role": "user", "content": "Test"}], [], sample_functions
            )

        # Test empty functions
        with pytest.raises(ValueError, match="Available functions dictionary cannot be empty"):
            client.chat_completion_with_tool_execution(
                [{"role": "user", "content": "Test"}], sample_tools, {}
            )

        # Test invalid max_iterations
        with pytest.raises(ValueError, match="Max iterations must be at least 1"):
            client.chat_completion_with_tool_execution(
                [{"role": "user", "content": "Test"}],
                sample_tools,
                sample_functions,
                max_iterations=0
            )

        with pytest.raises(ValueError, match="Max iterations cannot exceed 10"):
            client.chat_completion_with_tool_execution(
                [{"role": "user", "content": "Test"}],
                sample_tools,
                sample_functions,
                max_iterations=11
            )

    def test_tool_choice_options(self, mock_client, sample_tools):
        """Test different tool choice options."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Response"
        mock_message.tool_calls = None
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

        # Test auto tool choice
        result = client.chat_completion_with_tools(
            messages=messages,
            tools=sample_tools,
            tool_choice="auto"
        )
        assert result["content"] == "Response"

        # Test none tool choice
        result = client.chat_completion_with_tools(
            messages=messages,
            tools=sample_tools,
            tool_choice="none"
        )
        assert result["content"] == "Response"

        # Test specific tool choice
        result = client.chat_completion_with_tools(
            messages=messages,
            tools=sample_tools,
            tool_choice={"type": "function", "function": {"name": "get_weather"}}
        )
        assert result["content"] == "Response"

    def test_tool_execution_with_multiple_tools(self, sample_functions):
        """Test execution of multiple tools in parallel."""
        client = MistralAIClient(api_key="test_key")

        # Multiple tool calls
        tool_calls = [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "Paris, France"}'
                }
            },
            {
                "id": "call_2",
                "type": "function",
                "function": {
                    "name": "calculate",
                    "arguments": '{"expression": "25 + 35"}'
                }
            }
        ]

        result = client.execute_tool_calls(
            tool_calls=tool_calls,
            available_functions=sample_functions
        )

        # Verify multiple tool responses
        assert len(result) == 2

        # Verify first tool response
        assert result[0]["name"] == "get_weather"
        content1 = json.loads(result[0]["content"])
        assert content1["location"] == "Paris, France"

        # Verify second tool response
        assert result[1]["name"] == "calculate"
        content2 = json.loads(result[1]["content"])
        assert content2["result"] == 60

    def test_tool_execution_error_handling(self, sample_functions):
        """Test error handling in tool execution."""
        client = MistralAIClient(api_key="test_key")

        # Tool call that will cause an error (invalid expression)
        tool_call = {
            "id": "call_error",
            "type": "function",
            "function": {
                "name": "calculate",
                "arguments": '{"expression": "invalid expression"}'
            }
        }

        result = client.execute_tool_calls(
            tool_calls=[tool_call],
            available_functions=sample_functions
        )

        # Verify error response
        assert len(result) == 1
        content = json.loads(result[0]["content"])
        assert "error" in content
        assert content["success"] is False
        assert "invalid" in content["error"].lower()


class TestVisionCapabilities:
    """Test cases for vision functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Mistral client."""
        with patch("src.mistral_client.Mistral") as mock:
            yield mock

    @pytest.fixture
    def mock_vision_response(self):
        """Create mock vision API response."""
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "This image shows the Eiffel Tower in Paris, France. It's a famous landmark built in 1889 for the World's Fair. The tower is 330 meters tall and is one of the most recognizable structures in the world."
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 50
        mock_usage.completion_tokens = 150
        mock_response.usage = mock_usage

        return mock_response

    def test_vision_analysis_basic(self, mock_client, mock_vision_response):
        """Test basic image analysis."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.complete.return_value = mock_vision_response

        client = MistralAIClient(api_key="test_key")
        
        # Use binary data to avoid file path issues
        with patch("base64.b64encode") as mock_b64:
            mock_b64.return_value = b"fake_base64"
            result = client.vision_analysis(
                image_data=b"fake_image_bytes",
                prompt="Describe this image"
            )

        assert "content" in result
        assert "duration" in result
        assert "tokens" in result
        assert "model" in result
        assert "level" in result
        assert "parameters" in result
        assert "detail" in result

        assert result["content"].startswith("This image shows")
        assert result["tokens"]["total"] == 200
        assert result["detail"] == "high"  # default

    def test_vision_analysis_validation(self, mock_client):
        """Test input validation."""
        client = MistralAIClient(api_key="test_key")

        # Test empty image data
        with pytest.raises(ValueError, match="Image data cannot be empty"):
            client.vision_analysis("", "Describe")

        # Test invalid detail level
        with pytest.raises(ValueError, match="Invalid detail level"):
            client.vision_analysis("test.jpg", detail="invalid")

    def test_vision_analysis_image_formats(self, mock_client, mock_vision_response):
        """Test different image input formats."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.complete.return_value = mock_vision_response

        client = MistralAIClient(api_key="test_key")

        # Test URL format
        result = client.vision_analysis(
            image_data="https://example.com/image.jpg",
            prompt="Describe"
        )
        assert result["content"].startswith("This image shows")

        # Test file path format - mock both file existence and reading
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=b"fake_image_data")):
            result = client.vision_analysis(
                image_data="test.jpg",
                prompt="Describe"
            )
            assert result["content"].startswith("This image shows")

        # Test binary data format
        with patch("base64.b64encode") as mock_b64:
            mock_b64.return_value = b"fake_base64"
            result = client.vision_analysis(
                image_data=b"fake_image_bytes",
                prompt="Describe"
            )
            assert result["content"].startswith("This image shows")

    def test_vision_analysis_detail_levels(self, mock_client, mock_vision_response):
        """Test different detail levels."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.complete.return_value = mock_vision_response

        client = MistralAIClient(api_key="test_key")

        # Use binary data to avoid file path issues
        with patch("base64.b64encode") as mock_b64:
            mock_b64.return_value = b"fake_base64"
            
            for detail_level in ["low", "high", "auto"]:
                result = client.vision_analysis(
                    image_data=b"fake_image_bytes",
                    prompt="Describe",
                    detail=detail_level
                )
                assert result["detail"] == detail_level
                assert result["content"].startswith("This image shows")

    def test_vision_with_text(self, mock_client, mock_vision_response):
        """Test multimodal conversation."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.complete.return_value = mock_vision_response

        client = MistralAIClient(api_key="test_key")
        messages = [{"role": "user", "content": "What's in this image?"}]

        # Use binary data to avoid file path issues
        with patch("base64.b64encode") as mock_b64:
            mock_b64.return_value = b"fake_base64"
            result = client.vision_with_text(
                messages=messages,
                image_data=b"fake_image_bytes"
            )

        assert result["content"].startswith("This image shows")
        assert result["tokens"]["total"] == 200

    def test_vision_with_text_validation(self, mock_client):
        """Test multimodal conversation validation."""
        client = MistralAIClient(api_key="test_key")

        # Test empty messages
        with pytest.raises(ValueError, match="Messages list cannot be empty"):
            client.vision_with_text([], "test.jpg")

        # Test empty image data
        with pytest.raises(ValueError, match="Image data cannot be empty"):
            client.vision_with_text([{"role": "user", "content": "test"}], "")

    def test_vision_error_handling(self, mock_client):
        """Test error handling."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.complete.side_effect = Exception("Vision API error")

        client = MistralAIClient(api_key="test_key")

        # Use binary data to avoid file path issues
        with patch("base64.b64encode") as mock_b64:
            mock_b64.return_value = b"fake_base64"
            with pytest.raises(RuntimeError, match="Failed to process vision request"):
                client.vision_analysis(b"fake_image_bytes", "Describe")

    def test_vision_with_text_error_handling(self, mock_client):
        """Test multimodal error handling."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.complete.side_effect = Exception("Multimodal API error")

        client = MistralAIClient(api_key="test_key")

        # Use binary data to avoid file path issues
        with patch("base64.b64encode") as mock_b64:
            mock_b64.return_value = b"fake_base64"
            with pytest.raises(RuntimeError, match="Failed to process multimodal vision request"):
                client.vision_with_text(
                    [{"role": "user", "content": "test"}],
                    b"fake_image_bytes"
                )

    def test_prepare_image_data_validation(self, mock_client):
        """Test image data preparation validation."""
        client = MistralAIClient(api_key="test_key")

        # Test empty data
        with pytest.raises(ValueError, match="Image data cannot be empty"):
            client._prepare_image_data("")

        # Test unsupported format
        with pytest.raises(ValueError, match="Unsupported image data format"):
            client._prepare_image_data(12345)

    def test_prepare_image_data_formats(self, mock_client):
        """Test image data preparation for different formats."""
        client = MistralAIClient(api_key="test_key")

        # Test URL (should return unchanged)
        url = "https://example.com/image.jpg"
        result = client._prepare_image_data(url)
        assert result == url

        # Test file path (mock both existence and file reading)
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=b"fake_image_data")):
            result = client._prepare_image_data("test.jpg")
            assert result.startswith("data:image/jpeg;base64,")

        # Test binary data
        with patch("base64.b64encode") as mock_b64:
            mock_b64.return_value = b"fake_base64"
            result = client._prepare_image_data(b"fake_image_bytes")
            assert result.startswith("data:image/jpeg;base64,")
