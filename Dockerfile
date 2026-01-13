# Base stage: Common dependencies and code
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/models_cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data ./data
COPY py ./py
COPY config.yaml setup_env.sh ./

RUN dos2unix setup_env.sh

# UI Stage
FROM base AS ui

COPY start-ui.sh ./
RUN dos2unix start-ui.sh && chmod +x start-ui.sh

EXPOSE 8080
CMD ["./start-ui.sh"]

# MCP Stage
FROM base AS mcp

COPY start-mcp.sh ./
RUN dos2unix start-mcp.sh && chmod +x start-mcp.sh

EXPOSE 8080
CMD ["./start-mcp.sh"]