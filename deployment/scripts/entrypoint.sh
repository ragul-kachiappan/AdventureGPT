#!/bin/bash
set -e

# Function to check if a service is ready
wait_for_service() {
    local host="$1"
    local port="$2"
    local service="$3"
    
    echo "Waiting for $service to be ready..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$service is ready!"
}

# Wait for required services
wait_for_service postgres 5432 "PostgreSQL"
wait_for_service redis 6379 "Redis"
wait_for_service chroma 8000 "ChromaDB"

# Start the Starlette server in the background
echo "Starting Starlette server..."
uvicorn src.backend.api:app --host 0.0.0.0 --port 8000 &
STARLETTE_PID=$!

# Wait for Starlette to be ready
wait_for_service localhost 8000 "Starlette"

# Execute the command passed to the script
exec "$@" 