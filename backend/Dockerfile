# Use Python 3.11 slim as base for markitdown compatibility
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    poppler-utils \
    wget \
    unzip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install Playwright and Chromium dependencies
RUN pip install --no-cache-dir playwright \
  && playwright install chromium \
  && playwright install-deps chromium

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Alembic migrations directory
COPY alembic ./alembic

# Copy application code
COPY . ./

# Create directories for pipeline outputs and data
RUN mkdir -p output data

# Copy and set permissions for startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose the FastAPI port
EXPOSE 8000

# Run startup script on container start
ENTRYPOINT ["/start.sh"]
