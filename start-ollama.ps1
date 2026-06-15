# ============================================================
# start-ollama.ps1
# Starts the NL-to-SQL app with a local Gemma model via Ollama.
# No internet API key required for inference.
# ============================================================

Write-Host ""
Write-Host "=== NL-to-SQL Analytics Assistant (Local / Ollama Mode) ===" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# FIRST TIME ONLY — Copy .env from template
# ------------------------------------------------------------
if (-Not (Test-Path ".env")) {
    Write-Host "[First-time setup] Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "[First-time setup] .env created. MODEL_PROVIDER is already set to 'gemma'." -ForegroundColor Green
    Write-Host ""
}

# Ensure MODEL_PROVIDER is set to gemma in .env
$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch "MODEL_PROVIDER=gemma") {
    Write-Host "WARNING: MODEL_PROVIDER in .env is not set to 'gemma'." -ForegroundColor Yellow
    Write-Host "         Update .env:  MODEL_PROVIDER=gemma" -ForegroundColor White
    Write-Host ""
}

# ------------------------------------------------------------
# FIRST TIME ONLY — Build the Docker image
# (Skip with: $env:SKIP_BUILD="1" before running this script)
# ------------------------------------------------------------
if ($env:SKIP_BUILD -ne "1") {
    Write-Host "[First-time setup] Building Docker image..." -ForegroundColor Yellow
    Write-Host "  Tip: set `$env:SKIP_BUILD=1 to skip this step on subsequent runs." -ForegroundColor DarkGray
    docker compose --profile ollama build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker build failed. Exiting." -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# ------------------------------------------------------------
# EVERY RUN — Start both app + ollama containers
# ------------------------------------------------------------
Write-Host "Starting app + ollama containers..." -ForegroundColor Green
docker compose --profile ollama up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start containers. Exiting." -ForegroundColor Red
    exit 1
}

# ------------------------------------------------------------
# FIRST TIME ONLY — Pull the Gemma model inside the Ollama container
# This downloads ~5 GB and only needs to be done once.
# The model is stored in the 'ollama_models' Docker volume and
# persists across container restarts.
# ------------------------------------------------------------
Write-Host ""
Write-Host "Checking if gemma4:e4b model is already downloaded..." -ForegroundColor Yellow

$modelList = docker exec shop-ollama-1 ollama list 2>&1
if ($modelList -notmatch "gemma4:e4b") {
    Write-Host ""
    Write-Host "[First-time setup] Pulling gemma4:e4b model. This may take several minutes..." -ForegroundColor Yellow
    Write-Host "  This only runs once. The model is cached in a Docker volume for future starts." -ForegroundColor DarkGray
    Write-Host ""
    docker exec shop-ollama-1 ollama pull gemma4:e4b
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to pull gemma4:e4b model. Check that the ollama container is running." -ForegroundColor Red
        exit 1
    }
    Write-Host ""
    Write-Host "gemma4:e4b model downloaded successfully." -ForegroundColor Green
} else {
    Write-Host "gemma4:e4b model already present. Skipping download." -ForegroundColor Green
}

# ------------------------------------------------------------
# EVERY RUN — Attach to logs
# ------------------------------------------------------------
Write-Host ""
Write-Host "App is running at: http://localhost:8502" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop following logs (containers keep running)." -ForegroundColor DarkGray
Write-Host "To stop all containers run:  docker compose --profile ollama down" -ForegroundColor DarkGray
Write-Host ""

docker compose --profile ollama logs -f app
