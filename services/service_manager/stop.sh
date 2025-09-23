#!/bin/bash

# Service Manager Stop Script
# Stops the service manager and cleans up

set -e

echo "🛑 Stopping Service Manager..."

# Stop the service manager
if docker-compose ps | grep -q "service_manager"; then
    echo "🔄 Stopping containers..."
    docker-compose down
    echo "✅ Service Manager stopped"
else
    echo "ℹ️  Service Manager is not running"
fi

# Optionally remove the service network (commented out to avoid disrupting other services)
# echo "🧹 Cleaning up network..."
# docker network rm service_network 2>/dev/null || echo "ℹ️  Network was not removed (may be in use by other services)"

echo "🏁 Cleanup complete!"