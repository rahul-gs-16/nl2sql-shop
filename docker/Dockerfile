# ── NL-to-SQL Analytics Assistant ─────────────────────────────────────────
# Build:   docker build -f docker/Dockerfile -t nl2sql-shop-app:istore .
# Run:     docker compose up
# ---------------------------------------------------------------------------

FROM python:3.11-slim

# System dependencies for sentence-transformers native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Working directory inside the container
WORKDIR /app

# Install CPU-only torch before other deps so sentence-transformers
# does not pull in CUDA wheels (saves ~3 GB in the image)
RUN pip install --no-cache-dir \
    torch==2.6.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining Python dependencies (layer-cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY data/ ./data/

# Streamlit configuration — disable welcome message and telemetry
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV PYTHONPATH=/app
# Suppress ChromaDB anonymous telemetry (avoids posthog capture errors)
ENV ANONYMIZED_TELEMETRY=False
# Suppress torch.classes introspection warning from sentence-transformers
ENV TOKENIZERS_PARALLELISM=false

# Expose Streamlit's default port
EXPOSE 8501

# Entry point: create DB (if not mounted) then start Streamlit
CMD ["streamlit", "run", "app/ui/main.py", "--server.address=0.0.0.0", "--server.port=8501"]
