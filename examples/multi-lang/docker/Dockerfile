# Multi-stage Docker build for MCP Python SDK
FROM python:3.10-slim AS builder

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /build

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-dev

# Final stage
FROM python:3.10-slim

# Install uv in final image
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/pyproject.toml /build/uv.lock ./
COPY --from=builder /build/src ./src

# Set up environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Create a non-root user
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Default command (can be overridden)
CMD ["python", "-m", "mcp"]

# Example labels
LABEL maintainer="MCP SDK Team" \
      version="1.0.0" \
      description="MCP Python SDK Container" \
      org.opencontainers.image.source="https://github.com/modelcontextprotocol/python-sdk"
