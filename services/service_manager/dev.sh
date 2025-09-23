#!/bin/bash

# Development runner for Service Manager
# Runs the service directly with Go for faster development

set -e

echo "🔧 Starting Service Manager in development mode..."

# Check if Docker is running (still needed to manage other services)
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create service network if it doesn't exist
echo "📡 Creating service network..."
docker network create service_network 2>/dev/null || echo "✅ Network already exists"

# Build the Go binary
echo "🔨 Building Go application..."
go build -o service-manager main.go

# Set development environment
export PORT=9000
export GIN_MODE=debug

echo "🚀 Starting service manager on port $PORT..."
echo "🌐 Dashboard will be available at: http://localhost:$PORT"
echo "🔄 Press Ctrl+C to stop"
echo ""

# Run the service
./service-manager