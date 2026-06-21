#!/usr/bin/env bash
# ============================================================
# start-cloud.sh
# Starts the NL-to-SQL app using a cloud LLM provider.
# No Ollama / Gemma required.
# Supported providers: gemini, openai
# ============================================================

set -euo pipefail

echo ""
echo "=== NL-to-SQL Analytics Assistant (Cloud Mode) ==="
echo ""

# ------------------------------------------------------------
# FIRST TIME ONLY — Copy .env from template
# ------------------------------------------------------------
if [ ! -f ".env" ]; then
    echo "[First-time setup] Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "ACTION REQUIRED: Open .env and set your API key before continuing."
    echo "  For Gemini:  set GOOGLE_API_KEY=<your-key>  and  MODEL_PROVIDER=gemini"
    echo "  For ChatGPT: set OPENAI_API_KEY=<your-key>  and  MODEL_PROVIDER=openai"
    echo ""
    read -r -p "Press Enter once you have saved your .env file"
fi

# ------------------------------------------------------------
# FIRST TIME ONLY — Build the Docker image
# (Skip with: SKIP_BUILD=1 before running this script)
# ------------------------------------------------------------
if [ "${SKIP_BUILD:-}" != "1" ]; then
    echo "[First-time setup] Building Docker image..."
    echo "  Tip: set SKIP_BUILD=1 to skip this step on subsequent runs."
    docker compose build
    echo ""
fi

# ------------------------------------------------------------
# EVERY RUN — Start only the app container (no Ollama)
# ------------------------------------------------------------
echo "Starting app container..."
echo "  App will be available at: http://localhost:8502"
echo "  Press Ctrl+C to stop."
echo ""

docker compose up app
