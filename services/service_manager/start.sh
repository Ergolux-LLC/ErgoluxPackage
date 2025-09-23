#!/bin/bash

# Service Manager Startup Script
# This script sets up and starts the service manager

set -e

echo "🚀 Starting Service Manager..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create service network if it doesn't exist
echo "📡 Creating service network..."
docker network create service_network 2>/dev/null || echo "✅ Network already exists"

# Build and start the service manager
echo "🔨 Building and starting service manager..."
docker-compose up -d --build

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 5

# Check if service is running
if docker-compose ps | grep -q "service_manager.*Up"; then
    echo "✅ Service Manager is running!"
    echo "🌐 Access the dashboard at: http://localhost:9000"
    echo ""
    echo "📋 Available commands:"
    echo "  • View logs:    docker-compose logs -f service_manager"
    echo "  • Stop service: docker-compose down"
    echo "  • Restart:      docker-compose restart"
    echo ""
else
    echo "❌ Failed to start Service Manager"
    echo "📋 Check logs with: docker-compose logs service_manager"
    exit 1
fi