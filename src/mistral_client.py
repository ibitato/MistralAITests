"""
Mistral AI Client Module

This module provides a client for interacting with Mistral AI services.
"""

import json
import logging
import os
import time
from collections.abc import Generator
from typing import Any, Callable, Dict, List, Optional, Union

from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models import Function, Tool, ToolCall

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
    ) -> str:
        """Get chat completion from Mistral AI.

        Args:
            messages: List of chat messages
            temperature: Temperature for completion (0.0 to 1.0), optional
            determinism_level: Determinism level (1-5), optional

        Returns:
            Completion text

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
    ) -> dict[str, Any]:
        """Get chat completion with performance metrics.

        Args:
            messages: List of chat messages
            temperature: Temperature for completion (0.0 to 1.0), optional
            determinism_level: Determinism level (1-5), optional

        Returns:
            Dictionary containing:
            - content: The response text
            - duration: Request duration in seconds
            - tokens: Total tokens used (input + output)
            - model: Model used
            - level: Determinism level used
            - metrics: Additional performance metrics

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
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                **params
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
                    tool_calls.append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    })

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
                    "content": json.dumps({
                        "error": str(e),
                        "success": False,
                    }),
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
                all_messages.append({
                    "role": "tool",
                    "content": tool_response["content"],
                    "tool_call_id": tool_response["tool_call_id"],
                })

                tool_execution_history.append({
                    "function": tool_response["name"],
                    "arguments": json.loads(tool_response["content"]),
                    "success": "error" not in json.loads(tool_response["content"]),
                })

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
