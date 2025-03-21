# Use Python 3.10 slim as base image for smaller size while maintaining compatibility
FROM python:3.10-slim

# Add metadata labels
LABEL maintainer="PDangelmaier"
LABEL description="Model Context Protocol server for Paperless-ngx and n8n integration"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create a non-root user to run the application
RUN groupadd -r mcp && useradd -r -g mcp mcp

# Set working directory
WORKDIR /app

# Copy requirements file separately to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Set proper permissions
RUN chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Expose the port the MCP server will run on
EXPOSE 8000

# Set the command to run the server
CMD ["python", "-m", "src.mcp_server"]

# Health check to verify the server is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

