# Service Manager

A web-based interface for managing Docker Compose services in the Ergolux microservices project.

## Features

- **Visual Dashboard**: See all services at a glance with their current status
- **Service Control**: Start, stop, and restart services with a single click
- **Real-time Updates**: WebSocket-based live status updates every 5 seconds
- **Container Details**: View individual container status, ports, and health information
- **Log Viewing**: View service logs directly in the web interface
- **Responsive Design**: Bootstrap 5-based interface that works on mobile and desktop

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Go 1.21+ (for development)
- The service needs access to the Docker socket to manage other containers

### Running with Docker Compose

1. Navigate to the service manager directory:

   ```bash
   cd services/service_manager
   ```

2. Make sure the external network exists:

   ```bash
   docker network create service_network 2>/dev/null || true
   ```

3. Start the service manager:

   ```bash
   docker-compose up -d
   ```

4. Access the web interface:
   ```
   http://localhost:9000
   ```

### Running in Development Mode

1. Install dependencies:

   ```bash
   go mod tidy
   ```

2. Run the service:

   ```bash
   go run main.go
   ```

3. Access the web interface:
   ```
   http://localhost:9000
   ```

## How It Works

### Service Discovery

The service manager automatically discovers all Docker Compose services in the project by:

1. Scanning the `services/db/` directory for auto-generated database services
2. Scanning the `services/` directory for hand-crafted services
3. Looking for `docker-compose.yml` files in each service directory

### Status Monitoring

- **Running**: All containers are running
- **Stopped**: All containers are stopped
- **Partial**: Some containers are running, some are not
- **Error**: Unable to determine status

### Container Management

The service uses the Docker CLI to:

- Execute `docker compose ps` to check service status
- Execute `docker compose up -d` to start services
- Execute `docker compose down` to stop services
- Execute `docker compose logs` to retrieve logs

### Security Considerations

- The service requires access to the Docker socket (`/var/run/docker.sock`)
- In production, consider using Docker's TCP API with TLS for remote management
- The service runs as a non-root user when containerized
- All Docker operations are scoped to individual service directories

## API Endpoints

### GET /api/services

Returns a list of all discovered services with their current status.

### POST /api/services/{name}/start

Starts the specified service.

### POST /api/services/{name}/stop

Stops the specified service.

### POST /api/services/{name}/restart

Restarts the specified service.

### GET /api/services/{name}/logs?lines={n}

Returns the last N lines of logs for the specified service.

### GET /api/services/{name}/status

Returns detailed status information for a specific service.

### WebSocket /ws

Provides real-time service status updates.

## Configuration

Environment variables:

- `PORT`: Port to run the web server on (default: 9000)
- `GIN_MODE`: Gin framework mode (release/debug)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │ Service Manager │    │ Docker Services │
│                 │    │                 │    │                 │
│ Bootstrap UI    │◄──►│ Go + Gin + WS   │◄──►│ docker-compose  │
│ Real-time Updates│   │ Service Discovery│   │ Individual      │
└─────────────────┘    └─────────────────┘    │ Services        │
                                              └─────────────────┘
```

## Troubleshooting

### Service not discovered

- Ensure the service has a `docker-compose.yml` file
- Check that the service directory is under `services/` or `services/db/`

### Cannot start/stop services

- Verify Docker socket permissions
- Ensure the service manager has access to `/var/run/docker.sock`
- Check that Docker Compose is installed in the container

### WebSocket connection issues

- Check browser console for connection errors
- Verify the service is accessible on the configured port
- Ensure no firewall is blocking WebSocket connections

## Development

### Adding New Features

1. **Backend**: Modify `main.go` to add new API endpoints
2. **Frontend**: Update `templates/dashboard.html` for UI changes
3. **Styling**: Bootstrap 5 classes are used throughout

### Testing

```bash
# Test service discovery
curl http://localhost:9000/api/services

# Test service control
curl -X POST http://localhost:9000/api/services/auth/start

# Test log retrieval
curl "http://localhost:9000/api/services/auth/logs?lines=50"
```
