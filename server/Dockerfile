# Enhanced Threads Bot Backend - Python Application
# This is a Python application, NOT a Node.js application
# Railway deployment - Python backend only
# NO npm, NO node, NO frontend logic

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV PLATFORM=railway

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies ONLY
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (Python only)
COPY . .

# Create necessary directories
RUN mkdir -p config assets/images

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/status || exit 1

# Start the Python application ONLY
CMD ["python", "start.py"] 