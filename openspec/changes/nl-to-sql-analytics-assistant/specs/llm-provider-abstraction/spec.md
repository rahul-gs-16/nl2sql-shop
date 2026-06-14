## ADDED Requirements

### Requirement: Common LLM provider interface
The system SHALL define an abstract `LLMProvider` base class with a single `generate(prompt: str, temperature: float = 0) -> str` method. All LLM provider implementations MUST implement this interface.

#### Scenario: Provider generates a response
- **WHEN** the SQL generation layer calls `provider.generate(prompt)`
- **THEN** the active provider SHALL return a string containing the generated SQL

### Requirement: Gemma provider via Ollama
The system SHALL implement a `GemmaProvider` class that delegates to the Ollama HTTP API at the URL specified by `OLLAMA_BASE_URL`. It SHALL support the `gemma3` model.

#### Scenario: Gemma provider generates SQL
- **WHEN** `MODEL_PROVIDER=gemma` and Ollama is running with the gemma3 model
- **THEN** `GemmaProvider.generate(prompt)` SHALL return a valid SQL string from the Ollama API

#### Scenario: Ollama unavailable with Gemma selected
- **WHEN** `MODEL_PROVIDER=gemma` and Ollama is not reachable at `OLLAMA_BASE_URL`
- **THEN** the system SHALL raise a clear error at startup indicating Ollama is unavailable and SHALL NOT start the Streamlit UI

### Requirement: Gemini provider via Google API
The system SHALL implement a `GeminiProvider` class that uses the Google Generative AI API (`langchain-google-genai`) with a valid `GOOGLE_API_KEY`.

#### Scenario: Gemini provider generates SQL
- **WHEN** `MODEL_PROVIDER=gemini` and a valid `GOOGLE_API_KEY` is set
- **THEN** `GeminiProvider.generate(prompt)` SHALL return a valid SQL string from the Google API

### Requirement: OpenAI provider via OpenAI API
The system SHALL implement an `OpenAIProvider` class that uses the OpenAI API (`langchain-openai`) with a valid `OPENAI_API_KEY`.

#### Scenario: OpenAI provider generates SQL
- **WHEN** `MODEL_PROVIDER=openai` and a valid `OPENAI_API_KEY` is set
- **THEN** `OpenAIProvider.generate(prompt)` SHALL return a valid SQL string from the OpenAI API
