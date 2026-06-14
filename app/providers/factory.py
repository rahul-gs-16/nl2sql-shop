"""
app/providers/factory.py

Factory function that instantiates the correct LLM provider based on the
``MODEL_PROVIDER`` configuration value.
"""

from app.config import settings
from app.providers.base import LLMProvider


def get_provider(name: str | None = None) -> LLMProvider:
    """
    Return an instantiated :class:`LLMProvider` for the given provider name.

    Parameters
    ----------
    name : str | None
        Provider name: one of ``"gemma"``, ``"gemini"``, ``"openai"``.
        Defaults to ``settings.MODEL_PROVIDER`` when *None*.

    Returns
    -------
    LLMProvider
        The concrete provider instance.

    Raises
    ------
    ValueError
        If *name* is not a recognised provider.
    """
    provider_name = (name or settings.MODEL_PROVIDER).strip().lower()

    if provider_name == "gemma":
        from app.providers.gemma import GemmaProvider
        return GemmaProvider()

    if provider_name == "gemini":
        from app.providers.gemini import GeminiProvider
        return GeminiProvider()

    if provider_name == "openai":
        from app.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()

    valid = ", ".join(sorted(settings.VALID_PROVIDERS))
    raise ValueError(
        f"Unknown MODEL_PROVIDER '{provider_name}'. Valid options are: {valid}"
    )
