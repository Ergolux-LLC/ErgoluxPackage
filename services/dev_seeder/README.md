# Development Seeder Service

This service seeds your Ergolux microservices with development data to make local development easier and more consistent.

## Overview

The dev seeder creates realistic test data across all microservices in the proper dependency order:

1. **Auth Service** - Developer user account
2. **Workspace Service** - Sample workspaces and memberships
3. **Human Service** - People associated with workspaces
4. **Location Service** - Properties and addresses
5. **Transaction Service** - Real estate deals and transactions
6. **Communication Services** - Messages and events

## Quick Start

### Prerequisites

Make sure your core services are running:

```bash
# From the project root
cd infrastructure/shared-services
docker-compose up -d

# Start core microservices (auth, workspace, human, etc.)
# Each service in services/auth, services/db/* directories
```

### Run the Seeder

```bash
# From this directory (services/dev_seeder/)
./seed.sh
```

Or manually:

```bash
docker-compose --profile seeding up --abort-on-container-exit
```

## Developer User Credentials

The seeder creates a developer user account with these credentials:

- **Email**: `dev@example.com`
- **Password**: `devpassword123`
- **Name**: Dev User
- **ID**: `aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa`

Use these credentials to log into the frontend at `http://app.ergolux.io.localhost:5173/login`

## Commands

### Basic Usage

```bash
./seed.sh              # Build and run seeder
./seed.sh run          # Same as above
./seed.sh build        # Build Docker image only
./seed.sh logs         # View seeder logs
./seed.sh clean        # Clean up containers/images
./seed.sh help         # Show help
```

### Advanced Usage

```bash
# Run with specific profile
docker-compose --profile seeding up

# Run in development mode with full dataset
docker-compose --profile dev-full up

# Check logs in real-time
docker-compose logs -f dev_seeder
```

## Configuration

The seeder connects to services using these environment variables:

```bash
AUTH_SERVICE_URL=http://auth_service:8001
WORKSPACE_SERVICE_URL=http://workspace_service:8002
HUMAN_SERVICE_URL=http://human_service:8003
LOCATION_SERVICE_URL=http://location_service:8004
TRANSACTION_SERVICE_URL=http://transaction_service:8005
# ... etc
```

## How It Works

1. **Health Checks** - Waits for all services to be healthy before starting
2. **Dependency Order** - Creates data in the correct order to maintain relationships
3. **API-Based** - Uses actual service APIs, not direct database access
4. **Idempotent** - Can be run multiple times safely
5. **Logging** - Comprehensive logs to `/app/logs/dev_seeder.log`

## Current Status

✅ **Implemented:**

- Developer user account creation
- Service health checking
- Logging infrastructure
- Docker containerization

🚧 **In Progress:**

- Workspace seeding
- Human seeding
- Location seeding
- Transaction seeding
- Communication seeding

## Extending the Seeder

To add seeding for new services:

1. Add service URL to `docker-compose.yml` environment
2. Add health check to `ServiceHealthChecker`
3. Create new seeder class (e.g., `WorkspaceSeeder`)
4. Add to orchestration in `DevSeederOrchestrator.run_seeding()`

Example:

```python
class WorkspaceSeeder:
    def __init__(self, config, created_entities):
        self.config = config
        self.created_entities = created_entities

    async def seed_workspaces(self):
        # Implementation here
        pass
```

## Troubleshooting

### Services Not Ready

If seeder fails with service health checks:

```bash
# Check if services are running
docker ps

# Check service logs
docker-compose -f ../auth/docker-compose.yml logs
docker-compose -f ../db/workspace/docker-compose.yml logs
```

### Permission Errors

```bash
# Make sure script is executable
chmod +x seed.sh
```

### Network Issues

```bash
# Ensure service_network exists
docker network ls | grep service_network

# Create if missing
docker network create service_network
```

## Integration with Development Workflow

### Reset and Reseed

```bash
# Reset all databases and reseed
cd services/dev_seeder
./seed.sh clean
./seed.sh run
```

### CI/CD Integration

The seeder can be integrated into CI pipelines:

```yaml
# In GitHub Actions or similar
- name: Seed Development Data
  run: |
    cd services/dev_seeder
    ./seed.sh run
```

## Logs and Debugging

Logs are written to:

- Console output (Docker logs)
- `/app/logs/dev_seeder.log` (mounted volume)

View logs:

```bash
# Real-time logs
docker-compose logs -f dev_seeder

# From log files (if logging volume is mounted)
tail -f ./logs/dev_seeder.log
```

## Related Services

- **Auth Service** (`services/auth/`) - User authentication
- **Workspace Service** (`services/db/workspace/`) - Workspace management
- **Human Service** (`services/db/human/`) - People management
- **Frontend** (`frontend/`) - Web application using seeded data
