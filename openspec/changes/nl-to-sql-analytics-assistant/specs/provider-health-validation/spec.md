## ADDED Requirements

### Requirement: Validate provider health at application startup
The system SHALL validate the selected LLM provider's configuration at startup before serving any user requests. Validation SHALL check API key presence (for cloud providers) and Ollama reachability (for Gemma). Validation failures SHALL produce clear, actionable error messages and SHALL prevent the application from starting in a broken state.

#### Scenario: Valid cloud provider configuration at startup
- **WHEN** `MODEL_PROVIDER=gemini` or `MODEL_PROVIDER=openai` and the corresponding API key is present in the environment
- **THEN** the application SHALL start successfully

#### Scenario: Missing API key at startup
- **WHEN** `MODEL_PROVIDER=gemini` and `GOOGLE_API_KEY` is absent or empty
- **THEN** the application SHALL display an error message such as "GOOGLE_API_KEY is required for the Gemini provider" and SHALL NOT start the Streamlit UI

#### Scenario: Ollama unreachable with Gemma selected
- **WHEN** `MODEL_PROVIDER=gemma` and the Ollama service at `OLLAMA_BASE_URL` does not respond
- **THEN** the application SHALL display an error message indicating Ollama is unavailable and SHALL suggest using a cloud provider as an alternative

#### Scenario: Ollama unavailable with cloud provider selected
- **WHEN** `MODEL_PROVIDER=gemini` or `MODEL_PROVIDER=openai` and Ollama is not running
- **THEN** the application SHALL start successfully and the Gemma option SHALL be disabled or hidden in the UI
