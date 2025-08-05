# Use Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p assets/images config

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV PLATFORM=docker

# Expose port for health checks
EXPOSE 5000

# Start the application
CMD ["python", "start.py"] 