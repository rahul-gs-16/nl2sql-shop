## ADDED Requirements

### Requirement: Select LLM provider at runtime without code changes
The system SHALL read the `MODEL_PROVIDER` environment variable at startup to determine which LLM provider to activate. Valid values are `gemma`, `gemini`, and `openai`. The Streamlit UI SHALL also provide a dropdown for provider selection. Switching providers SHALL require only a configuration change, not a code change.

#### Scenario: Provider selected via environment variable
- **WHEN** `MODEL_PROVIDER=gemini` is set in the environment
- **THEN** the application SHALL instantiate and use `GeminiProvider` for all SQL generation requests

#### Scenario: Provider selected via Streamlit dropdown
- **WHEN** a user selects a different provider from the Streamlit dropdown
- **THEN** the application SHALL switch to that provider for subsequent queries within the same session

#### Scenario: Invalid provider value
- **WHEN** `MODEL_PROVIDER` is set to an unrecognized value
- **THEN** the application SHALL fail at startup with a clear message listing valid provider options
