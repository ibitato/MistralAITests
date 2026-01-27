"""
Determinism Controller for Mistral AI.

This module provides a controller to manage determinism levels for Mistral AI models.
"""

from typing import TypedDict


class DeterminismParameters(TypedDict):
    """Type definition for determinism parameters."""

    temperature: float
    top_p: float
    frequency_penalty: float
    presence_penalty: float


class DeterminismController:
    """Controller for managing determinism levels in Mistral AI models.

    Provides 5 predefined levels of control over text generation,
    from most exact (deterministic) to most free (creative).
    """

    def __init__(self, level: int = 3):
        """Initialize the determinism controller.

        Args:
            level: Determinism level (1-5), default is 3 (balanced)

        Raises:
            ValueError: If level is not between 1 and 5
        """
        if level not in range(1, 6):
            raise ValueError("Determinism level must be between 1 and 5")
        self.level = level

    def get_parameters(self) -> DeterminismParameters:
        """Get the parameters for the current determinism level.

        Returns:
            Dictionary with determinism parameters
        """
        levels = {
            1: {  # Most exact/deterministic
                "temperature": 0.0,
                "top_p": 1.0,  # Mistral API requires top_p=1 when using greedy sampling (temp=0)
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
            },
            2: {  # Very focused
                "temperature": 0.1,
                "top_p": 0.2,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
            },
            3: {  # Balanced (default)
                "temperature": 0.3,
                "top_p": 0.5,
                "frequency_penalty": 0.2,
                "presence_penalty": 0.2,
            },
            4: {  # Creative
                "temperature": 0.5,
                "top_p": 0.7,
                "frequency_penalty": 0.3,
                "presence_penalty": 0.3,
            },
            5: {  # Most free/creative
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.5,
                "presence_penalty": 0.5,
            },
        }

        return levels[self.level]  # type: ignore

    def get_level_description(self) -> str:
        """Get description of the current determinism level.

        Returns:
            Description of the current level
        """
        descriptions = {
            1: "Exact: Deterministic generation, minimal variation, ideal for consistent responses",
            2: "Focused: Highly controlled generation, minimal creativity",
            3: "Balanced: Balanced generation between precision and creativity",
            4: "Creative: Generation with more freedom, more variations",
            5: "Free: Highly creative generation, maximum variation",
        }

        return descriptions[self.level]

    def set_level(self, level: int) -> None:
        """Set a new determinism level.

        Args:
            level: New determinism level (1-5)

        Raises:
            ValueError: If level is not between 1 and 5
        """
        if level not in range(1, 6):
            raise ValueError("Determinism level must be between 1 and 5")
        self.level = level
