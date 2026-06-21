"""
app/providers/gemini.py

LLM provider implementation backed by the Google Generative AI API (Gemini).
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from app.config import settings
from app.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    """
    LLM provider that uses the Google Generative AI (Gemini) API.

    Requires ``settings.GOOGLE_API_KEY`` to be set. Health validation is
    performed at startup by ``app.providers.health.validate_provider``.
    """

    def __init__(self) -> None:
        self._llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
        )

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Send *prompt* to the Gemini API and return the response text.

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
        response = self._llm.invoke([HumanMessage(content=prompt)])
        return response.content
