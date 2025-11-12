# Multi-language MCP Development Container
FROM python:3.11-slim

LABEL maintainer="MCP Python SDK"
LABEL description="Multi-language container for MCP development with Python, Ruby, and Node.js support"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build essentials
    build-essential \
    curl \
    git \
    # Ruby dependencies
    ruby \
    ruby-dev \
    # Node.js dependencies
    nodejs \
    npm \
    # Additional utilities
    vim \
    less \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Ruby bundler
RUN gem install bundler

# Install global npm packages
RUN npm install -g typescript ts-node

# Set working directory
WORKDIR /workspace

# Copy project files
COPY . /workspace/

# Install Python dependencies using uv
RUN uv sync --frozen

# Install Ruby dependencies if Gemfile exists
RUN if [ -f "examples/ruby/Gemfile" ]; then \
    cd examples/ruby && bundle install; \
    fi

# Create directories for development
RUN mkdir -p /workspace/examples \
    /workspace/tests \
    /workspace/.vscode

# Expose ports for development servers
EXPOSE 8000 3000 4000

# Set entrypoint
CMD ["/bin/bash"]
