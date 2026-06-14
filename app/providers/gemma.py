"""
app/providers/gemma.py

LLM provider implementation backed by Ollama (local Gemma model).
"""

from langchain_ollama import OllamaLLM

from app.config import settings
from app.providers.base import LLMProvider


class GemmaProvider(LLMProvider):
    """
    LLM provider that delegates to a locally running Ollama instance.

    Requires Ollama to be reachable at ``settings.OLLAMA_BASE_URL`` with the
    ``gemma3`` model pulled. Health validation is performed separately at
    startup by ``app.providers.health.validate_provider``.
    """

    def __init__(self) -> None:
        self._llm = OllamaLLM(
            model="gemma4:e4b",
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0,
        )

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Send *prompt* to the Ollama Gemma3 model and return the response text.

        Parameters
        ----------
        prompt : str
            Full prompt string.
        temperature : float
            Sampling temperature forwarded to the Ollama API.

        Returns
        -------
        str
            The model's plain-text response.
        """
        self._llm.temperature = temperature
        result = self._llm.invoke(prompt)
        return str(result)
