"""
app/providers/health.py

Startup health validation for each LLM provider.
Checks API key presence (cloud providers) and Ollama reachability (Gemma).
"""

import logging
import requests

from app.config import settings

logger = logging.getLogger(__name__)


def validate_provider(name: str | None = None) -> bool:
    """
    Validate that the selected LLM provider is correctly configured.

    For cloud providers this checks that the required API key is present.
    For Gemma this checks that Ollama is reachable at ``settings.OLLAMA_BASE_URL``.

    Parameters
    ----------
    name : str | None
        Provider name to validate. Defaults to ``settings.MODEL_PROVIDER``.

    Returns
    -------
    bool
        ``True`` if valid. Raises on fatal misconfiguration.

    Raises
    ------
    RuntimeError
        If a required API key is missing or Ollama is unreachable for the
        Gemma provider.
    ValueError
        If *name* is not a recognised provider.
    """
    provider_name = (name or settings.MODEL_PROVIDER).strip().lower()

    if provider_name not in settings.VALID_PROVIDERS:
        valid = ", ".join(sorted(settings.VALID_PROVIDERS))
        raise ValueError(
            f"Unknown MODEL_PROVIDER '{provider_name}'. Valid options: {valid}"
        )

    if provider_name == "gemini":
        _check_api_key("GOOGLE_API_KEY", settings.GOOGLE_API_KEY, "gemini")

    elif provider_name == "openai":
        _check_api_key("OPENAI_API_KEY", settings.OPENAI_API_KEY, "openai")

    elif provider_name == "gemma":
        _check_ollama_reachable()

    return True


def is_ollama_available() -> bool:
    """
    Return ``True`` if the Ollama service responds within a short timeout.

    Does NOT raise — intended for non-fatal checks (e.g., disabling the
    Gemma dropdown when a cloud provider is selected).
    """
    try:
        resp = requests.get(settings.OLLAMA_BASE_URL, timeout=2)
        return resp.status_code < 500
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _check_api_key(env_var: str, value: str, provider: str) -> None:
    """Raise RuntimeError if *value* is empty or whitespace."""
    if not value or not value.strip():
        raise RuntimeError(
            f"{env_var} is required for the '{provider}' provider but is not set. "
            f"Add it to your .env file: {env_var}=<your-key>"
        )


def _check_ollama_reachable() -> None:
    """Raise RuntimeError if Ollama cannot be reached within 3 seconds."""
    url = settings.OLLAMA_BASE_URL
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code >= 500:
            raise RuntimeError(
                f"Ollama at '{url}' returned HTTP {resp.status_code}. "
                "Ensure the Ollama service is running and the gemma4:e4b model is pulled."
            )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Cannot reach Ollama at '{url}'. "
            "Start the Ollama service (docker compose up ollama) or switch to a cloud provider "
            "(MODEL_PROVIDER=gemini or MODEL_PROVIDER=openai)."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"Connection to Ollama at '{url}' timed out. "
            "Check that the service is running and accessible."
        )
