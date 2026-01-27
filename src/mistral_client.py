"""
Mistral AI Client Module

This module provides a client for interacting with Mistral AI services.
"""

import os
from typing import Any

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
        """
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

        chat_response = self.client.chat.complete(
            model=self.model, messages=messages, **params
        )
        return (
            str(chat_response.choices[0].message.content)
            if chat_response.choices
            and len(chat_response.choices) > 0
            and chat_response.choices[0].message.content
            else ""
        )

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
