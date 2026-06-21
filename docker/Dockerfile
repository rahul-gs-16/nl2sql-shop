# ── NL-to-SQL Analytics Assistant ─────────────────────────────────────────
# Build:   docker build -f docker/Dockerfile -t nl-sql-app .
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

# Install Python dependencies first (layer-cache friendly)
# REQUIREMENTS_FILE can be overridden at build time (e.g. requirements_cpu.txt)
ARG REQUIREMENTS_FILE=requirements.txt
COPY requirements.txt requirements_cpu.txt ./
RUN pip install --no-cache-dir -r ${REQUIREMENTS_FILE}

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
