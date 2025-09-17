# Ergolux Microservices Portal

This repository contains the core microservices and supporting infrastructure for the Ergolux SaaS platform, powering the portal at [app.ergolux.io](https://app.ergolux.io). The platform is designed for professionals in transaction-based industries such as real estate, escrow, title, and notary services.

## Architecture Overview

- **Microservices Structure:**

  - Each domain (e.g., communication_event, conversation, human, location, transaction, workspace, etc.) is implemented as a separate service under `services/` or `db/`.
  - Services in `db/` are auto-generated using the `db_service_generator/render_microservice.py` script.
  - Each service typically contains its own `docker-compose.yml`, `Dockerfile`, and `app/` directory with FastAPI or similar Python code.
  - Shared infrastructure and scripts are located in the `infrastructure/` and `scripts/` directories.

- **Development & Testing:**

  - Use the provided shell scripts in `infrastructure/scripts/` to start, stop, or manage core and service containers (`start-all.sh`, `start-core.sh`, etc.).
  - Each service has its own `requirements.txt` and may include a `test_endpoints.py` for endpoint testing.
  - The `_tests&docs_/loki-demo/` directory contains an example logging and monitoring setup (not used in production).

- **API & Integration:**
  - API definitions and test collections are managed in the `bruno/API/` directory.
  - The `web_bff/` folder contains the backend-for-frontend (BFF) service, acting as an API gateway for the web portal.

## Key Directories

- `services/` — Main business logic microservices
- `db/` — Auto-generated database-backed microservices (see `db_service_generator/`)
- `web_bff/` — Backend-for-frontend API gateway
- `infrastructure/` — Shared infrastructure and scripts
- `bruno/` — API definitions and test collections
- `_tests&docs_/loki-demo/` — Example logging/monitoring setup (not for production)

## Getting Started

1. Clone the repository.
2. Use the scripts in `infrastructure/scripts/` to start all services:
   ```sh
   ./infrastructure/scripts/start-all.sh
   ```
3. Access the portal at [app.ergolux.io](https://app.ergolux.io) (or your local deployment).

## Contributing

- Follow the structure and conventions of existing services when adding new microservices.
- Use the provided templates in `db_service_generator/` for rapid service scaffolding.
- See individual service `README.md` files (if present) for service-specific details.

---

For more details, review the code in each service directory, the `db_service_generator/` for service generation, and the scripts in `infrastructure/scripts/`.
