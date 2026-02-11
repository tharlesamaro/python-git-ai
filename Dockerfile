FROM python:3.13-slim

WORKDIR /app

# Install git (required for GitService tests) and UV
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

# Configure git for tests
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test User" && \
    git config --global init.defaultBranch main

# Copy project files
COPY pyproject.toml uv.lock .python-version ./
COPY src/ src/
COPY hooks/ hooks/
COPY tests/ tests/

# Install dependencies
RUN uv sync --frozen

# Default: run tests
CMD ["uv", "run", "pytest"]
