# ZergBot Demo Dockerfile
# Usage: docker run -p 8080:8080 zergbot/demo

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir -e .

# Set demo mode environment variables
ENV ZERGBOT_DEMO_MODE=1
ENV PYTHONUNBUFFERED=1

# Expose web demo port
EXPOSE 8080

# Create demo workspace
RUN mkdir -p /root/.zergbot/demo

# Default command: run web demo
CMD ["zergbot", "demo", "--web", "--port", "8080"]
