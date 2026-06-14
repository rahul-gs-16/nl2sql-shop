# ============================================================
# start-cloud.ps1
# Starts the NL-to-SQL app using a cloud LLM provider.
# No Ollama / Gemma required.
# Supported providers: gemini, openai
# ============================================================

Write-Host ""
Write-Host "=== NL-to-SQL Analytics Assistant (Cloud Mode) ===" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# FIRST TIME ONLY — Copy .env from template
# ------------------------------------------------------------
if (-Not (Test-Path ".env")) {
    Write-Host "[First-time setup] Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "ACTION REQUIRED: Open .env and set your API key before continuing." -ForegroundColor Red
    Write-Host "  For Gemini:  set GOOGLE_API_KEY=<your-key>  and  MODEL_PROVIDER=gemini" -ForegroundColor White
    Write-Host "  For ChatGPT: set OPENAI_API_KEY=<your-key>  and  MODEL_PROVIDER=openai" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter once you have saved your .env file"
}

# ------------------------------------------------------------
# FIRST TIME ONLY — Build the Docker image
# (Skip with: $env:SKIP_BUILD="1" before running this script)
# ------------------------------------------------------------
if ($env:SKIP_BUILD -ne "1") {
    Write-Host "[First-time setup] Building Docker image..." -ForegroundColor Yellow
    Write-Host "  Tip: set `$env:SKIP_BUILD=1 to skip this step on subsequent runs." -ForegroundColor DarkGray
    docker compose build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker build failed. Exiting." -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# ------------------------------------------------------------
# EVERY RUN — Start only the app container (no Ollama)
# ------------------------------------------------------------
Write-Host "Starting app container..." -ForegroundColor Green
Write-Host "  App will be available at: http://localhost:8502" -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

docker compose up app
