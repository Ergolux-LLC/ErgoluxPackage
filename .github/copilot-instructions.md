# Ergolux Microservices Portal - AI Coding Instructions

## Architecture Overview

This is a microservices-based SaaS platform for transaction professionals (real estate, escrow, title, notary) with distinct architectural patterns:

### Service Types & Patterns

1. **Auto-generated DB services** (`services/db/`) - CRUD microservices generated from schema definitions
2. **Auth service** (`services/auth/`) - Clean architecture with domain/application/infrastructure layers
3. **Service Manager** (`services/service_manager/`) - Go-based web dashboard for service management
4. **Shared Infrastructure** (`infrastructure/shared-services/`) - Redis, PostgreSQL, RabbitMQ
5. **Other services** (`services/web_bff/`, `services/account_setup/`) - FastAPI + Pydantic with simple structure
6. **Frontend** (`frontend/`) - Vite/SvelteKit app with TypeScript, Bootstrap, and environment-aware configuration

### Auto-Generated DB Services

**Pattern:** FastAPI + SQLAlchemy ORM with standardized structure

- Generated from `db_service_generator/render_microservice.py` using Jinja2 templates
- Schema definitions in `db_service_generator/tables.py` with fields, types, and ports
- Each service gets its own PostgreSQL container and dedicated port
- Standard CRUD endpoints with workspace-scoped operations
- Template files in `db_service_generator/template_for_db_tables/`
- Generated structure includes: models/, routes/, schemas/, use_cases/, interfaces/

### Auth Service (Clean Architecture Only)

**Pattern:** Domain-driven design with clean architecture layers

- `domain/` - Pure business logic with `@dataclass` models (see `services/auth/app/domain/user.py`)
- `application/use_case/` - Business use cases and orchestration
- `infrastructure/` - Framework-specific code and external integrations
- `interfaces/` - Adapter pattern for database, Redis, email connections

### Other Hand-Crafted Services

**Pattern:** FastAPI + Pydantic with simple structure

- Direct FastAPI routing with Pydantic models for validation
- SQLAlchemy for database operations without complex abstractions
- Example: `services/account_setup/` uses basic routes.py + models.py structure
- No domain/application layer separation

### Service Manager

**Pattern:** Go + Gin web framework with Bootstrap 5 UI (`services/service_manager/`)

- Web-based dashboard for managing all Docker Compose services in the project
- Automatic service discovery from `services/`, `infrastructure/shared-services/`, and `frontend/`
- Real-time status monitoring via WebSocket connections
- Docker CLI integration for start/stop/restart operations
- Log viewing interface with configurable line counts

**Usage:**

```bash
cd services/service_manager && ./dev.sh    # Development mode
cd services/service_manager && ./start.sh  # Docker deployment
```

**Access:** Web dashboard at `http://localhost:9000`

### Shared Services Infrastructure

**Pattern:** Centralized infrastructure services (`infrastructure/shared-services/`)

- Redis (port 6379) - Session storage and caching for auth service
- PostgreSQL (port 5432) - Shared database for cross-service data
- RabbitMQ (ports 5672, 15672) - Message queuing with management UI
- All services connected to `service_network` and `shared_services` networks
- Integrated with centralized logging via `logging_service-logs` volume

**Management:**

```bash
cd infrastructure/shared-services && docker-compose up -d    # Start all
cd infrastructure/shared-services && docker-compose down    # Stop all
```

**Dependencies:** Services requiring Redis (like auth) depend on shared-services being running

### Logging Aggregation

**Pattern:** Centralized log collection via Loki + Promtail + Grafana

- `services/logging/` - Log aggregation infrastructure with Loki (storage), Promtail (collection), Grafana (visualization)
- All services write logs to shared volume `logging_service-logs` mounted at `/app/logs/`
- Service-specific log files: `/app/logs/{service_name}.log`
- Access logs via `./logs.sh` script with commands: `query`, `tail`, `query {service_name}`

**Adding logging to new services:**

1. **Configure logging in main.py:**

```python
import logging
import os

# Create logs directory
os.makedirs("/app/logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler("/app/logs/{service_name}.log")  # File output
    ]
)
```

2. **Mount shared volume in docker-compose.yml:**

```yaml
volumes:
  - logging_service-logs:/app/logs
```

3. **Add external volume reference:**

```yaml
volumes:
  logging_service-logs:
    external: true
```

**Log viewing:** Use `cd services/logging && ./logs.sh query {service_name}` for service-specific logs or `./logs.sh tail` for real-time monitoring

### Critical Development Commands

**Generate new CRUD service:**

```bash
cd db_service_generator && python render_microservice.py
```

This reads `tables.py` schema and generates complete service in `services/db/[table_name]/`

**Service management:** Each service runs via individual `docker-compose.yml` files

- Infrastructure scripts in `infrastructure/scripts/` are currently empty
- Services use `service_network` Docker network for inter-service communication

**Testing:** Each generated service includes `test_endpoints.py` for endpoint validation

### Frontend Development

**Development workflow:**

```bash
cd frontend && npm run dev        # Development mode (direct)
cd frontend && npm run dev:prod   # Production mode locally
cd frontend && ./dev.sh          # Alternative dev script with port management
cd frontend && docker-compose up -d  # Docker service with hot reloading
```

**Docker service features:**

- Containerized Vite development server with immediate file change response
- Volume mounts for hot reloading: `src/`, `static/`, config files
- Integrated with centralized logging via `/app/logs/frontend.log`
- Optimized Vite config with polling for Docker file watching
- Service discovery via `service_network` and managed by service manager

**Key frontend features:**

- TypeScript throughout with strict typing
- Bootstrap 5.3+ for styling with Bootstrap Icons
- Environment-aware API configuration (`src/lib/config/environment.ts`)
- Modular API client (`src/lib/api/client.ts`) with service-specific methods
- SvelteKit file-based routing in `src/routes/`
- Shared components and utilities in `src/lib/`

### Frontend Integration

**Vite/SvelteKit Frontend** (`frontend/`)

- Modern SvelteKit application with TypeScript and Bootstrap styling
- Runs on localhost:5173 via `npm run dev` (configured in CORS)
- Environment-aware configuration with `.env` files for different modes
- API client with built-in connection to web_bff service
- Development script (`dev.sh`) handles port management and server restart
- Structure: `src/lib/` for shared components, API clients, and configuration
- Alternative ports: localhost:3000, localhost:8080 also allowed in web_bff CORS
- Handles authentication, workspace management, and service orchestration

### Data Flow & Integration

**Web BFF Pattern:** `services/web_bff/` acts as API gateway

- Routes in `app/routes/` correspond to frontend views and service proxying
- Example: `views.py` proxies human directory operations to `human_service:8000`
- Uses `httpx` for service-to-service HTTP communication
- Simple FastAPI + Pydantic structure (not clean architecture)

**Workspace-scoped data:** All services include `workspace_id` for tenant isolation

**Service discovery:** Container-to-container communication via Docker network names

### Environment & Configuration

**Container networking:** All services use `service_network` Docker network
**Database pattern:** Each DB service gets dedicated PostgreSQL container with standard env vars

- Format: `{table_name}_db` container, `{table_name}_service` application container
- Environment variables: `DB_HOST`, `DB_USER`, `POSTGRES_PASSWORD`, etc.
  **Configuration:** `.env` files in service root directories with service-specific settings

### API Documentation & Testing

**Bruno collections** in `bruno/API/Microservices/` provide comprehensive API documentation

- Organized by service domain (Human, Location, Transaction, etc.)
- Essential for understanding service endpoints and data contracts
- Use for testing and integration validation

**Note:** `_tests&docs_/` directory contains reference materials for AI development only - not used in production

### Code Generation Conventions

When adding new entities to the platform:

1. **Define schema** in `db_service_generator/tables.py`:

   - Specify fields, SQLAlchemy types, Pydantic types, and service port
   - Include required `workspace_id` field for tenant isolation
   - Follow naming: `{table_name}` becomes `{table_name}_service`

2. **Generate service** via `render_microservice.py`:

   - Creates complete microservice with CRUD operations
   - Generates Docker containers, models, routes, schemas, use cases
   - Auto-creates test endpoints with default workspace_id: `aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa`

3. **Service structure**:
   - SQLAlchemy ORM models in `models/`
   - FastAPI routes in `routes/`
   - Pydantic schemas in `schemas/`
   - Business logic in `use_cases/`
   - Database adapters in `interfaces/relationaldb/`

### Database Patterns & Development

**Generated services:** Use SQLAlchemy ORM with `Base.metadata.create_all()` auto-table creation
**Auth service:** Uses SQLAlchemy Core with explicit table definitions and `User.from_row()` mapping  
**Other services:** Direct SQLAlchemy ORM without abstraction layers
**Development mode:** `ENV=dev` drops and recreates all tables on startup for fresh state

### Schema Management

**Canonical source:** `db_service_generator/tables.py` contains all entity definitions

- Field specifications include SQLAlchemy types, Pydantic validation, required/optional status
- Port assignments for each service (8002-8009 currently used)
- Enum types defined for complex fields (USState, TransactionPhase, etc.)

**Template system:** `db_service_generator/template_for_db_tables/` contains Jinja2 templates

- Consistent structure across all generated services
- Includes Docker configuration, test endpoints, and full application structure
- Templates ensure uniform error handling, logging, and validation patterns

Always check `tables.py` for the canonical schema definitions and `template_for_db_tables/` for the latest generation patterns when working with the platform.
