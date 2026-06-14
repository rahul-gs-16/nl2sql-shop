"""
app/providers/base.py

Abstract base class that all LLM provider implementations must extend.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Common interface for all LLM provider implementations.

    Each concrete provider wraps a specific LLM backend (Ollama, Google API,
    OpenAI API) and exposes a single ``generate`` method so that business logic
    remains completely decoupled from SDK-specific calls.
    """

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Generate a text response for the given prompt.

        Parameters
        ----------
        prompt : str
            The full prompt string to send to the underlying model.
        temperature : float
            Sampling temperature (0 = deterministic, higher = more creative).

        Returns
        -------
        str
            The model's text response.
        """
