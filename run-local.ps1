# ============================================================
# run-local.ps1
# Sets up a local Python virtual environment, installs the 
# necessary dependencies, and runs the Streamlit application.
# ============================================================

Write-Host "=== Apple Store Assistant (Local Mode) ===" -ForegroundColor Cyan
Write-Host ""

# 1. Setup Virtual Environment
if (-Not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}

# 2. Activate Virtual Environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
. .\.venv\Scripts\Activate.ps1

# 3. Install Requirements
Write-Host "Installing requirements from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

# 4. Initialize Database
Write-Host "Initializing inventory database..." -ForegroundColor Yellow
python scripts/create_db.py

# 5. Run the Streamlit App
Write-Host ""
Write-Host "Starting Streamlit app..." -ForegroundColor Green
Write-Host "The app will be available at: http://localhost:8501" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

streamlit run app/ui/main.py
