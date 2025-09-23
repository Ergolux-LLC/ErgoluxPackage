#!/bin/bash

# Development Seeder Script for Ergolux Microservices
# This script runs the development data seeder service

set -e

echo "🌱 Ergolux Development Seeder"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the dev_seeder directory."
    exit 1
fi

# Parse command line arguments
ACTION=${1:-"run"}

case $ACTION in
    "run")
        print_status "Building and running development seeder..."
        
        # Build the seeder service
        print_status "Building seeder Docker image..."
        docker-compose build
        
        # Run the seeder
        print_status "Starting seeding process..."
        docker-compose --profile seeding up --abort-on-container-exit
        
        # Check exit code
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 0 ]; then
            print_success "Seeding completed successfully!"
        else
            print_error "Seeding failed with exit code $EXIT_CODE"
            exit $EXIT_CODE
        fi
        ;;
        
    "build")
        print_status "Building seeder Docker image..."
        docker-compose build
        print_success "Build completed!"
        ;;
        
    "logs")
        print_status "Showing seeder logs..."
        docker-compose logs dev_seeder
        ;;
        
    "clean")
        print_status "Cleaning up seeder containers and images..."
        docker-compose down --rmi all --volumes --remove-orphans
        print_success "Cleanup completed!"
        ;;
        
    "help"|"-h"|"--help")
        echo "Usage: $0 [ACTION]"
        echo ""
        echo "Actions:"
        echo "  run     - Build and run the development seeder (default)"
        echo "  build   - Build the seeder Docker image only"
        echo "  logs    - Show seeder logs"
        echo "  clean   - Clean up containers and images"
        echo "  help    - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              # Run seeder"
        echo "  $0 run          # Run seeder"
        echo "  $0 build        # Build only"
        echo "  $0 logs         # View logs"
        echo "  $0 clean        # Clean up"
        ;;
        
    *)
        print_error "Unknown action: $ACTION"
        print_status "Use '$0 help' to see available actions"
        exit 1
        ;;
esac