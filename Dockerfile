# Recommended base image: Lightweight and compatible with AI libraries
FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Ensures logs are flushed immediately to the console
# HF_HOME: Sets a custom directory for Hugging Face models so they are easy to locate
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/models_cache

WORKDIR /app

# Install system dependencies
# 'git' is often required for certain pip packages or langchain integrations
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy folders "data" and "py", along with config and scripts
COPY data ./data
COPY py ./py
COPY config.yaml setup_env.sh startup.sh ./
COPY nginx.conf /etc/nginx/sites-available/default

# Make the startup script executable
RUN chmod +x startup.sh

# Expose port 80 for Nginx
EXPOSE 80

# Run the "startup.sh"
CMD ["./startup.sh"]