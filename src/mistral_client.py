"""
Mistral AI Client Module

This module provides a client for interacting with Mistral AI services.
"""

import os

from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models import AssistantMessage, SystemMessage, UserMessage

# Load environment variables
load_dotenv()


class MistralAIClient:
    """Client for Mistral AI API."""

    def __init__(self, api_key: str | None = None, model: str = "mistral-tiny"):
        """Initialize Mistral AI client.

        Args:
            api_key: Mistral AI API key. If None, uses MISTRAL_AI_API_KEY from .env
            model: Model to use for completions
        """
        self.api_key = api_key or os.getenv("MISTRAL_AI_API_KEY")
        self.model = model
        self.client = Mistral(api_key=self.api_key)

    def chat_completion(
        self,
        messages: list[UserMessage | AssistantMessage | SystemMessage],
        temperature: float = 0.7,
    ) -> str:
        """Get chat completion from Mistral AI.

        Args:
            messages: List of chat messages
            temperature: Temperature for completion (0.0 to 1.0)

        Returns:
            Completion text
        """
        chat_response = self.client.chat.complete(
            model=self.model, messages=messages, temperature=temperature
        )
        return chat_response.choices[0].message.content

    def embeddings(self, text: str) -> list[float]:
        """Get embeddings for text.

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        embeddings_response = self.client.embeddings(model="mistral-embed", input=text)
        return embeddings_response.data[0].embedding

    def list_models(self) -> list[str]:
        """List available models.

        Returns:
            List of available model names
        """
        models = self.client.models.list()
        return [model.id for model in models.data]
