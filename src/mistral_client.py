"""
Mistral AI Client Module

This module provides a client for interacting with Mistral AI services.
"""

import base64
import json
import logging
import os
import time
from collections.abc import Callable, Generator
from typing import Any, Literal

from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models import (
    AssistantMessage,
    Function,
    ImageURL,
    ImageURLChunk,
    SystemMessage,
    Tool,
    ToolMessage,
    UserMessage,
)

from src.determinism_controller import DeterminismController

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class MistralAIClient:
    """Client for Mistral AI API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "mistral-tiny",
        determinism_level: int = 3,
    ):
        """Initialize Mistral AI client.

        Args:
            api_key: Mistral AI API key. If None, uses MISTRAL_AI_API_KEY from .env
            model: Model to use for completions
            determinism_level: Determinism level (1-5), default is 3 (balanced)
        """
        self.api_key = api_key or os.getenv("MISTRAL_AI_API_KEY")
        self.model = model
        self.determinism_level = determinism_level
        self.client = Mistral(api_key=self.api_key)
        self.determinism_controller = DeterminismController(determinism_level)

    def chat_completion(
        self,
        messages: list[Any],
        temperature: float | None = None,
        determinism_level: int | None = None,
        reasoning: bool = False,
    ) -> str:
        """Get chat completion from Mistral AI.

        Args:
            messages: List of chat messages
            temperature: Temperature for completion (0.0 to 1.0), optional
            determinism_level: Determinism level (1-5), optional
            reasoning: Enable reasoning mode to show thinking process, optional

        Returns:
            Completion text (includes reasoning steps if reasoning=True)

        Raises:
            ValueError: If messages are empty or invalid
            RuntimeError: If API request fails or returns invalid response
        """
        # Validate messages
        if not messages or len(messages) == 0:
            raise ValueError("Messages list cannot be empty")

        # Use the specified determinism level or fall back to client default
        level = (
            determinism_level
            if determinism_level is not None
            else self.determinism_level
        )

        # Update determinism controller level if different from current
        if level != self.determinism_controller.level:
            self.determinism_controller.set_level(level)

        params = self.determinism_controller.get_parameters()

        # If temperature is explicitly provided, override the level's temperature
        if temperature is not None:
            params["temperature"] = temperature
            # When temperature is 0 (greedy sampling), Mistral API requires top_p=1
            if temperature == 0.0:
                params["top_p"] = 1.0

        # Add reasoning prompt if enabled
        if reasoning:
            # Add reasoning instruction to system message or create one
            has_system = any(msg.get("role") == "system" for msg in messages)
            if not has_system:
                messages.insert(
                    0,
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that thinks step by step. Show your reasoning process before providing the final answer.",
                    },
                )
            else:
                # Modify existing system message to include reasoning
                for msg in messages:
                    if msg.get("role") == "system":
                        msg[
                            "content"
                        ] += " Show your reasoning process step by step before providing the final answer."
                        break

        try:
            chat_response = self.client.chat.complete(
                model=self.model, messages=messages, **params
            )

            if not chat_response.choices or len(chat_response.choices) == 0:
                raise RuntimeError("API returned empty choices")

            if not chat_response.choices[0].message.content:
                raise RuntimeError("API returned empty message content")

            return str(chat_response.choices[0].message.content)

        except Exception as e:
            raise RuntimeError(f"Failed to get chat completion: {str(e)}") from e

    def chat_completion_stream(
        self,
        messages: list[Any],
        temperature: float | None = None,
        determinism_level: int | None = None,
    ) -> Generator[str, None, None]:
        """Get streaming chat completion from Mistral AI.

        Args:
            messages: List of chat messages
            temperature: Temperature for completion (0.0 to 1.0), optional
            determinism_level: Determinism level (1-5), optional

        Returns:
            Generator that yields response chunks as they arrive

        Raises:
            ValueError: If messages are empty or invalid
            RuntimeError: If API request fails or streaming is interrupted

        Example:
            ```python
            for chunk in client.chat_completion_stream(messages):
                print(chunk, end='', flush=True)
            ```
        """
        # Validate messages
        if not messages or len(messages) == 0:
            raise ValueError("Messages list cannot be empty")

        # Use the specified determinism level or fall back to client default
        level = (
            determinism_level
            if determinism_level is not None
            else self.determinism_level
        )

        # Update determinism controller level if different from current
        if level != self.determinism_controller.level:
            self.determinism_controller.set_level(level)

        params = self.determinism_controller.get_parameters()

        # If temperature is explicitly provided, override the level's temperature
        if temperature is not None:
            params["temperature"] = temperature
            # When temperature is 0 (greedy sampling), Mistral API requires top_p=1
            if temperature == 0.0:
                params["top_p"] = 1.0

        try:
            # Use streaming API
            for chunk in self.client.chat.stream(
                model=self.model, messages=messages, **params
            ):
                # Handle different chunk types for streaming
                try:
                    # For mock objects in tests
                    if (
                        hasattr(chunk, "choices")
                        and chunk.choices
                        and len(chunk.choices) > 0
                    ):
                        choice = chunk.choices[0]
                        if hasattr(choice, "delta") and hasattr(
                            choice.delta, "content"
                        ):
                            content = choice.delta.content
                            if content:
                                yield content
                    # For real Pydantic models
                    elif hasattr(chunk, "model_dump"):
                        chunk_dict = chunk.model_dump()
                        if isinstance(chunk_dict, dict):
                            choices = chunk_dict.get("choices")
                            if choices and len(choices) > 0:
                                choice = choices[0]
                                if isinstance(choice, dict):
                                    delta = choice.get("delta")
                                    if isinstance(delta, dict):
                                        content = delta.get("content")
                                        if content:
                                            yield content
                    # For direct content
                    elif hasattr(chunk, "content"):
                        content = chunk.content
                        if content:
                            yield content
                except Exception as e:
                    print(f"Error processing stream chunk: {str(e)}")
                    continue

        except Exception as e:
            raise RuntimeError(f"Streaming failed: {str(e)}") from e

    def chat_completion_with_metrics(
        self,
        messages: list[Any],
        temperature: float | None = None,
        determinism_level: int | None = None,
        reasoning: bool = False,
    ) -> dict[str, Any]:
        """Get chat completion with performance metrics.

        Args:
            messages: List of chat messages
            temperature: Temperature for completion (0.0 to 1.0), optional
            determinism_level: Determinism level (1-5), optional
            reasoning: Enable reasoning mode to show thinking process, optional

        Returns:
            Dictionary containing:
            - content: The response text (includes reasoning if enabled)
            - duration: Request duration in seconds
            - tokens: Total tokens used (input + output)
            - model: Model used
            - level: Determinism level used
            - metrics: Additional performance metrics
            - reasoning_enabled: Whether reasoning was used

        Raises:
            ValueError: If messages are empty or invalid
            RuntimeError: If API request fails
        """
        # Validate messages
        if not messages or len(messages) == 0:
            raise ValueError("Messages list cannot be empty")

        start_time = time.time()

        # Use the specified determinism level or fall back to client default
        level = (
            determinism_level
            if determinism_level is not None
            else self.determinism_level
        )

        # Update determinism controller level if different from current
        if level != self.determinism_controller.level:
            self.determinism_controller.set_level(level)

        params = self.determinism_controller.get_parameters()

        # If temperature is explicitly provided, override the level's temperature
        if temperature is not None:
            params["temperature"] = temperature
            # When temperature is 0 (greedy sampling), Mistral API requires top_p=1
            if temperature == 0.0:
                params["top_p"] = 1.0

        # Add reasoning prompt if enabled
        if reasoning:
            # Add reasoning instruction to system message or create one
            has_system = any(msg.get("role") == "system" for msg in messages)
            if not has_system:
                messages.insert(
                    0,
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that thinks step by step. Show your reasoning process before providing the final answer.",
                    },
                )
            else:
                # Modify existing system message to include reasoning
                for msg in messages:
                    if msg.get("role") == "system":
                        msg[
                            "content"
                        ] += " Show your reasoning process step by step before providing the final answer."
                        break

        try:
            chat_response = self.client.chat.complete(
                model=self.model, messages=messages, **params
            )

            duration = time.time() - start_time

            if not chat_response.choices or len(chat_response.choices) == 0:
                raise RuntimeError("API returned empty choices")

            if not chat_response.choices[0].message.content:
                raise RuntimeError("API returned empty message content")

            # Calculate token usage
            prompt_tokens = (
                chat_response.usage.prompt_tokens if chat_response.usage else 0
            )
            completion_tokens = (
                chat_response.usage.completion_tokens if chat_response.usage else 0
            )
            total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

            return {
                "content": str(chat_response.choices[0].message.content),
                "duration": duration,
                "tokens": {
                    "total": total_tokens,
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                },
                "model": self.model,
                "level": level,
                "parameters": params,
                "metrics": {
                    "tokens_per_second": total_tokens / duration if duration > 0 else 0,
                    "response_time_ms": duration * 1000,
                },
                "reasoning_enabled": reasoning,
            }

        except Exception as e:
            raise RuntimeError(
                f"Failed to get chat completion with metrics: {str(e)}"
            ) from e

    def embeddings(self, text: str) -> list[float]:
        """Get embeddings for text.

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        embeddings_response = self.client.embeddings.create(
            model="mistral-embed", inputs=[text]
        )
        if embeddings_response.data and len(embeddings_response.data) > 0:
            embedding = embeddings_response.data[0].embedding
            return embedding if embedding else [0.0]
        return [0.0]

    def list_models(self) -> list[str]:
        """List available models.

        Returns:
            List of available model names
        """
        models = self.client.models.list()
        return [model.id for model in models.data] if models.data else []

    def chat_completion_with_tools(
        self,
        messages: list[Any],
        tools: list[Function],
        temperature: float | None = None,
        determinism_level: int | None = None,
        tool_choice: str = "auto",
    ) -> dict[str, Any]:
        """Get chat completion with tool calling capabilities.

        Args:
            messages: List of chat messages
            tools: List of Function objects defining available tools
            temperature: Temperature for completion (0.0 to 1.0), optional
            determinism_level: Determinism level (1-5), optional
            tool_choice: Tool choice behavior ('auto', 'none', or specific tool name)

        Returns:
            Dictionary containing:
            - content: The response text (may be None if tool calls are made)
            - tool_calls: List of tool calls made by the model
            - duration: Request duration in seconds
            - tokens: Token usage information
            - model: Model used
            - level: Determinism level used

        Raises:
            ValueError: If messages are empty or tools are invalid
            RuntimeError: If API request fails
        """
        # Validate messages
        if not messages or len(messages) == 0:
            raise ValueError("Messages list cannot be empty")

        # Validate tools
        if not tools or len(tools) == 0:
            raise ValueError("Tools list cannot be empty")

        # Use the specified determinism level or fall back to client default
        level = (
            determinism_level
            if determinism_level is not None
            else self.determinism_level
        )

        # Update determinism controller level if different from current
        if level != self.determinism_controller.level:
            self.determinism_controller.set_level(level)

        params = self.determinism_controller.get_parameters()

        # If temperature is explicitly provided, override the level's temperature
        if temperature is not None:
            params["temperature"] = temperature
            # When temperature is 0 (greedy sampling), Mistral API requires top_p=1
            if temperature == 0.0:
                params["top_p"] = 1.0

        start_time = time.time()

        try:
            # Convert tools to proper format
            tools_list = None
            if tools:
                tools_list = [
                    (
                        Tool(type="function", function=tool)
                        if isinstance(tool, Function)
                        else tool
                    )
                    for tool in tools
                ]

            # Convert tool_choice to proper literal type
            tool_choice_str: Literal["auto", "none", "any", "required"] = "auto"
            if isinstance(tool_choice, str):
                tool_choice_str = tool_choice  # type: ignore
            elif isinstance(tool_choice, dict):
                tool_choice_str = "auto"  # Simplified for mypy

            chat_response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                tools=tools_list,
                tool_choice=tool_choice_str,
                **params,
            )

            duration = time.time() - start_time

            if not chat_response.choices or len(chat_response.choices) == 0:
                raise RuntimeError("API returned empty choices")

            choice = chat_response.choices[0]
            message = choice.message

            # Extract content (may be None if tool calls are made)
            content = message.content if message.content else None

            # Extract tool calls
            tool_calls = []
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_calls.append(
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                    )

            # Calculate token usage
            prompt_tokens = (
                chat_response.usage.prompt_tokens if chat_response.usage else 0
            )
            completion_tokens = (
                chat_response.usage.completion_tokens if chat_response.usage else 0
            )
            total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

            return {
                "content": content,
                "tool_calls": tool_calls,
                "duration": duration,
                "tokens": {
                    "total": total_tokens,
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                },
                "model": self.model,
                "level": level,
                "parameters": params,
            }

        except Exception as e:
            raise RuntimeError(
                f"Failed to get chat completion with tools: {str(e)}"
            ) from e

    def execute_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
        available_functions: dict[str, Callable],
    ) -> list[dict[str, Any]]:
        """Execute tool calls using available functions.

        Args:
            tool_calls: List of tool calls from the model
            available_functions: Dictionary mapping function names to callable functions

        Returns:
            List of tool responses with results or errors

        Raises:
            ValueError: If tool calls or functions are invalid
            RuntimeError: If tool execution fails
        """
        if not tool_calls or len(tool_calls) == 0:
            raise ValueError("Tool calls list cannot be empty")

        if not available_functions or len(available_functions) == 0:
            raise ValueError("Available functions dictionary cannot be empty")

        tool_responses = []

        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])
            tool_call_id = tool_call["id"]

            try:
                # Get the function from available functions
                if function_name not in available_functions:
                    raise ValueError(f"Function {function_name} not available")

                function = available_functions[function_name]

                # Execute the function
                function_result = function(**function_args)

                # Create tool response
                tool_response = {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_result),
                }

                tool_responses.append(tool_response)

            except Exception as e:
                # Create error response
                error_response = {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(
                        {
                            "error": str(e),
                            "success": False,
                        }
                    ),
                }
                tool_responses.append(error_response)

        return tool_responses

    def chat_completion_with_tool_execution(
        self,
        messages: list[Any],
        tools: list[Function],
        available_functions: dict[str, Callable],
        temperature: float | None = None,
        determinism_level: int | None = None,
        max_iterations: int = 3,
    ) -> dict[str, Any]:
        """Complete chat with automatic tool execution.

        This method handles the full tool calling workflow:
        1. Get initial response (may include tool calls)
        2. Execute any tool calls
        3. Send tool responses back to model
        4. Repeat until no more tool calls or max iterations reached

        Args:
            messages: List of chat messages
            tools: List of Function objects defining available tools
            available_functions: Dictionary mapping function names to callable functions
            temperature: Temperature for completion (0.0 to 1.0), optional
            determinism_level: Determinism level (1-5), optional
            max_iterations: Maximum number of tool calling iterations

        Returns:
            Dictionary containing final response and execution details

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If execution fails
        """
        if not messages or len(messages) == 0:
            raise ValueError("Messages list cannot be empty")

        if not tools or len(tools) == 0:
            raise ValueError("Tools list cannot be empty")

        if not available_functions or len(available_functions) == 0:
            raise ValueError("Available functions dictionary cannot be empty")

        if max_iterations < 1:
            raise ValueError("Max iterations must be at least 1")

        if max_iterations > 10:
            raise ValueError("Max iterations cannot exceed 10")

        all_messages = messages.copy()
        iteration = 0
        tool_execution_history = []

        while iteration < max_iterations:
            iteration += 1

            # Get response with tools
            response = self.chat_completion_with_tools(
                messages=all_messages,
                tools=tools,
                temperature=temperature,
                determinism_level=determinism_level,
                tool_choice="auto",
            )

            # Add assistant response to message history
            assistant_message = {
                "role": "assistant",
                "content": response["content"],
            }

            if response["tool_calls"]:
                assistant_message["tool_calls"] = response["tool_calls"]

            all_messages.append(assistant_message)

            # If no tool calls, we're done
            if not response["tool_calls"]:
                break

            # Execute tool calls
            tool_responses = self.execute_tool_calls(
                tool_calls=response["tool_calls"],
                available_functions=available_functions,
            )

            # Add tool responses to message history and execution history
            for tool_response in tool_responses:
                all_messages.append(
                    {
                        "role": "tool",
                        "content": tool_response["content"],
                        "tool_call_id": tool_response["tool_call_id"],
                    }
                )

                tool_execution_history.append(
                    {
                        "function": tool_response["name"],
                        "arguments": json.loads(tool_response["content"]),
                        "success": "error" not in json.loads(tool_response["content"]),
                    }
                )

        # Get final response (without tools)
        final_response = self.chat_completion_with_tools(
            messages=all_messages,
            tools=tools,
            temperature=temperature,
            determinism_level=determinism_level,
            tool_choice="none",  # Force final answer without more tool calls
        )

        return {
            "final_response": final_response["content"],
            "all_messages": all_messages,
            "tool_execution_history": tool_execution_history,
            "iterations": iteration,
            "tokens_used": final_response["tokens"]["total"],
            "duration": final_response["duration"],
        }

    def _prepare_image_data(self, image_data: str | bytes) -> str:
        """Prepare image data for vision API.

        Args:
            image_data: Image file path, URL, or binary data

        Returns:
            Base64 encoded image data or URL

        Raises:
            ValueError: If image data is invalid or unsupported format
        """
        if not image_data or (isinstance(image_data, str) and not image_data.strip()):
            raise ValueError("Image data cannot be empty")

        # If it's already a URL, return as-is
        if isinstance(image_data, str) and (
            image_data.startswith("http://") or image_data.startswith("https://")
        ):
            return image_data

        # If it's a file path, read the file
        if isinstance(image_data, str) and os.path.exists(image_data):
            try:
                with open(image_data, "rb") as image_file:
                    image_data = image_file.read()
            except OSError as e:
                raise ValueError(f"Could not read image file: {str(e)}") from e

        # If it's binary data, encode as base64
        if isinstance(image_data, bytes):
            try:
                # Convert to base64
                return f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
            except Exception as e:
                raise ValueError(f"Could not encode image data: {str(e)}") from e

        raise ValueError(
            "Unsupported image data format. Provide file path, URL, or binary data."
        )

    def vision_analysis(
        self,
        image_data: str | bytes,
        prompt: str = "",
        temperature: float | None = None,
        determinism_level: int | None = None,
        detail: str = "high",
    ) -> dict[str, Any]:
        """Analyze images with vision capabilities.

        Args:
            image_data: Image file path, URL, or binary data
            prompt: Optional text prompt for multimodal analysis
            temperature: Creativity level (0.0 to 1.0), optional
            determinism_level: Determinism level (1-5), optional
            detail: Analysis detail level ("low", "high", "auto")

        Returns:
            Dictionary containing:
            - content: Analysis results
            - duration: Request duration in seconds
            - tokens: Token usage information
            - model: Model used
            - level: Determinism level used
            - parameters: Parameters used

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If API request fails
        """
        # Validate image data
        if not image_data or (isinstance(image_data, str) and not image_data.strip()):
            raise ValueError("Image data cannot be empty")

        # Validate detail level
        valid_detail_levels = ["low", "high", "auto"]
        if detail not in valid_detail_levels:
            raise ValueError(
                f"Invalid detail level. Must be one of: {valid_detail_levels}"
            )

        # Prepare image data
        try:
            prepared_image = self._prepare_image_data(image_data)
        except ValueError as e:
            raise ValueError(f"Invalid image data: {str(e)}") from e

        # Use the specified determinism level or fall back to client default
        level = (
            determinism_level
            if determinism_level is not None
            else self.determinism_level
        )

        # Update determinism controller level if different from current
        if level != self.determinism_controller.level:
            self.determinism_controller.set_level(level)

        params = self.determinism_controller.get_parameters()

        # If temperature is explicitly provided, override the level's temperature
        if temperature is not None:
            params["temperature"] = temperature
            # When temperature is 0 (greedy sampling), Mistral API requires top_p=1
            if temperature == 0.0:
                params["top_p"] = 1.0

        start_time = time.time()

        try:
            # Prepare messages for vision API
            messages: list[
                SystemMessage | UserMessage | AssistantMessage | ToolMessage
            ] = []

            # Add system message if there's a prompt
            if prompt:
                messages.append(UserMessage(role="user", content=prompt))

            # Add image message
            if prepared_image.startswith("http"):
                # URL format
                messages.append(
                    UserMessage(
                        role="user",
                        content=[ImageURLChunk(image_url=ImageURL(url=prepared_image))],
                    )
                )
            else:
                # Base64 format
                messages.append(
                    UserMessage(
                        role="user",
                        content=[ImageURLChunk(image_url=ImageURL(url=prepared_image))],
                    )
                )

            # Call vision API
            chat_response = self.client.chat.complete(
                model=self.model, messages=messages, **params
            )

            duration = time.time() - start_time

            if not chat_response.choices or len(chat_response.choices) == 0:
                raise RuntimeError("API returned empty choices")

            choice = chat_response.choices[0]
            message = choice.message

            # Extract content
            content = message.content if message.content else ""

            # Calculate token usage
            prompt_tokens = (
                chat_response.usage.prompt_tokens if chat_response.usage else 0
            )
            completion_tokens = (
                chat_response.usage.completion_tokens if chat_response.usage else 0
            )
            total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

            return {
                "content": content,
                "duration": duration,
                "tokens": {
                    "total": total_tokens,
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                },
                "model": self.model,
                "level": level,
                "parameters": params,
                "detail": detail,
            }

        except Exception as e:
            raise RuntimeError(f"Failed to process vision request: {str(e)}") from e

    def vision_with_text(
        self,
        messages: list[Any],
        image_data: str | bytes,
        temperature: float | None = None,
        determinism_level: int | None = None,
    ) -> dict[str, Any]:
        """Multimodal conversation with vision and text.

        Args:
            messages: Chat messages (can include text and image references)
            image_data: Image to analyze
            temperature: Creativity level (0.0 to 1.0), optional
            determinism_level: Determinism level (1-5), optional

        Returns:
            Dictionary with response and metrics

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If API request fails
        """
        # Validate messages
        if not messages or len(messages) == 0:
            raise ValueError("Messages list cannot be empty")

        # Validate image data
        if not image_data or (isinstance(image_data, str) and not image_data.strip()):
            raise ValueError("Image data cannot be empty")

        # Prepare image data
        try:
            prepared_image = self._prepare_image_data(image_data)
        except ValueError as e:
            raise ValueError(f"Invalid image data: {str(e)}") from e

        # Use the specified determinism level or fall back to client default
        level = (
            determinism_level
            if determinism_level is not None
            else self.determinism_level
        )

        # Update determinism controller level if different from current
        if level != self.determinism_controller.level:
            self.determinism_controller.set_level(level)

        params = self.determinism_controller.get_parameters()

        # If temperature is explicitly provided, override the level's temperature
        if temperature is not None:
            params["temperature"] = temperature
            # When temperature is 0 (greedy sampling), Mistral API requires top_p=1
            if temperature == 0.0:
                params["top_p"] = 1.0

        start_time = time.time()

        try:
            # Prepare multimodal messages
            multimodal_messages: list[
                SystemMessage | UserMessage | AssistantMessage | ToolMessage
            ] = []

            # Add existing text messages
            for message in messages:
                if isinstance(message, dict):
                    # Convert dict messages to proper types
                    if message.get("role") == "system":
                        multimodal_messages.append(SystemMessage(**message))
                    elif message.get("role") == "user":
                        multimodal_messages.append(UserMessage(**message))
                    elif message.get("role") == "assistant":
                        multimodal_messages.append(AssistantMessage(**message))
                    elif message.get("role") == "tool":
                        multimodal_messages.append(ToolMessage(**message))
                else:
                    multimodal_messages.append(message)

            # Add image message
            if prepared_image.startswith("http"):
                # URL format
                multimodal_messages.append(
                    UserMessage(
                        role="user",
                        content=[ImageURLChunk(image_url=ImageURL(url=prepared_image))],
                    )
                )
            else:
                # Base64 format
                multimodal_messages.append(
                    UserMessage(
                        role="user",
                        content=[ImageURLChunk(image_url=ImageURL(url=prepared_image))],
                    )
                )

            # Call vision API
            chat_response = self.client.chat.complete(
                model=self.model, messages=multimodal_messages, **params
            )

            duration = time.time() - start_time

            if not chat_response.choices or len(chat_response.choices) == 0:
                raise RuntimeError("API returned empty choices")

            choice = chat_response.choices[0]
            message = choice.message

            # Extract content
            content = message.content if message.content else ""

            # Calculate token usage
            prompt_tokens = (
                chat_response.usage.prompt_tokens if chat_response.usage else 0
            )
            completion_tokens = (
                chat_response.usage.completion_tokens if chat_response.usage else 0
            )
            total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

            return {
                "content": content,
                "duration": duration,
                "tokens": {
                    "total": total_tokens,
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                },
                "model": self.model,
                "level": level,
                "parameters": params,
            }

        except Exception as e:
            raise RuntimeError(
                f"Failed to process multimodal vision request: {str(e)}"
            ) from e


# Regenerated with Black 26.3.0
