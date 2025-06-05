FROM python:3.12.8-slim as builder

# Set workdir
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Copy only dependency files first
COPY ./pyproject.toml ./uv.lock ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --group docker --no-dev --no-install-project

# Start final image
FROM python:3.12.8-slim

WORKDIR /app

# Install only required system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-openbsd \
    postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Copy application code and scripts
COPY ./src ./src
COPY ./pyproject.toml ./uv.lock ./
COPY ./deployment/scripts/entrypoint.sh ./scripts/entrypoint.sh
COPY ./deployment/scripts/startup.sh ./scripts/startup.sh

# Create necessary directories
RUN mkdir -p /var/run/redis && \
    mkdir -p /var/lib/chromadb

# Make scripts executable
RUN chmod +x ./scripts/*

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["/app/scripts/startup.sh"]
