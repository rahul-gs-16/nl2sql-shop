"""
app/providers/openai_provider.py

LLM provider implementation backed by the OpenAI API (GPT family).
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.config import settings
from app.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    LLM provider that uses the OpenAI Chat Completions API.

    Requires ``settings.OPENAI_API_KEY`` to be set. Health validation is
    performed at startup by ``app.providers.health.validate_provider``.
    """

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Send *prompt* to the OpenAI API and return the response text.

        Parameters
        ----------
        prompt : str
            Full prompt string.
        temperature : float
            Sampling temperature.

        Returns
        -------
        str
            The model's plain-text response.
        """
        llm = self._llm.bind(temperature=temperature)
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
