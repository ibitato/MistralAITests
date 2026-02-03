"""
Mistral AI Client Module

This module provides a client for interacting with Mistral AI services.
"""

import os
import time
from typing import Any, Generator, Iterator

from dotenv import load_dotenv
from mistralai import Mistral

from src.determinism_controller import DeterminismController

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
            for chunk in self.client.chat.complete_stream(
                model=self.model, messages=messages, **params
            ):
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
        
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
            prompt_tokens = chat_response.usage.prompt_tokens if chat_response.usage else 0
            completion_tokens = chat_response.usage.completion_tokens if chat_response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            
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
                }
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to get chat completion with metrics: {str(e)}") from e

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
