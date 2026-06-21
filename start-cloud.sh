#!/bin/bash

# ============================================================
# start-cloud.sh
# Starts the NL-to-SQL app using a cloud LLM provider.
# No Ollama / Gemma required.
# Supported providers: gemini, openai
# ============================================================

# Define color codes for Mac Terminal
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
WHITE='\033[1;37m'
GREEN='\033[1;32m'
DARKGRAY='\033[1;30m' # Might render as dark gray or standard gray depending on terminal theme
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}=== NL-to-SQL Analytics Assistant (Cloud Mode) ===${NC}"
echo ""

# ------------------------------------------------------------
# FIRST TIME ONLY — Copy .env from template
# ------------------------------------------------------------
if [ ! -f ".env" ]; then
    # Added the safety check we discussed earlier
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}[First-time setup] Creating .env from .env.example...${NC}"
        cp .env.example .env
        echo ""
        echo -e "${RED}ACTION REQUIRED: Open .env and set your API key before continuing.${NC}"
        echo -e "${WHITE}  For Gemini:  GOOGLE_API_KEY=<your-key>  and  MODEL_PROVIDER=gemini${NC}"
        echo -e "${WHITE}  For ChatGPT: OPENAI_API_KEY=<your-key>  and  MODEL_PROVIDER=openai${NC}"
        echo ""
        read -p "Press Enter once you have saved your .env file"
    else
        echo -e "${RED}[Error] Cannot create .env because '.env.example' is missing from this directory.${NC}"
    fi
fi

# ------------------------------------------------------------
# FIRST TIME ONLY — Create the SQLite database if missing
# ------------------------------------------------------------
if [ ! -f "data/inventory.db" ]; then
    echo -e "${YELLOW}[First-time setup] Creating inventory database...${NC}"
    python3 scripts/create_db.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}Database creation failed. Exiting.${NC}"
        exit 1
    fi
    echo ""
fi

# ------------------------------------------------------------
# FIRST TIME ONLY — Build the Docker image
# (Skip with: SKIP_BUILD="1" ./start-cloud.sh)
# ------------------------------------------------------------
if [ "$SKIP_BUILD" != "1" ]; then
    echo -e "${YELLOW}[First-time setup] Building Docker image (CPU-only, no CUDA)...${NC}"
    echo -e "${DARKGRAY}  Tip: run 'SKIP_BUILD=1 ./start-cloud.sh' to skip this step on subsequent runs.${NC}"

    docker compose build --build-arg REQUIREMENTS_FILE=requirements_cpu.txt

    # Check if the previous command (docker build) failed
    if [ $? -ne 0 ]; then
        echo -e "${RED}Docker build failed. Exiting.${NC}"
        exit 1
    fi
    echo ""
fi

# ------------------------------------------------------------
# EVERY RUN — Start only the app container (no Ollama)
# ------------------------------------------------------------
echo -e "${GREEN}Starting app container...${NC}"
echo -e "${CYAN}  App will be available at: http://localhost:8502${NC}"
echo -e "${DARKGRAY}  Press Ctrl+C to stop.${NC}"
echo ""

docker compose up app