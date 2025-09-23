# Ergolux Logging Service

This service provides centralized log aggregation for all Ergolux microservices using Loki, Promtail, and Grafana.

## Architecture

- **Loki**: Log aggregation system that stores and indexes logs
- **Promtail**: Log shipping agent that collects logs from services and sends them to Loki
- **Grafana**: Optional web UI for advanced log visualization and dashboards

## Quick Start

1. **Start the logging service:**

   ```bash
   cd services/logging
   docker-compose up -d
   ```

2. **View logs in terminal:**

   ```bash
   # Tail all service logs
   ./logs.sh tail

   # Tail only web_bff logs
   ./logs.sh tail web_bff

   # Show recent logs
   ./logs.sh query

   # Show only errors and warnings
   ./logs.sh errors
   ```

3. **Access Grafana (optional):**
   - URL: http://localhost:33000
   - Username: admin
   - Password: admin

## Service Integration

To integrate a service with the logging system:

1. **Add logging volume to service's docker-compose.yml:**

   ```yaml
   volumes:
     - service-logs:/app/logs
   ```

2. **Configure service to write logs to file:**

   ```python
   import logging

   # Configure file logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
       handlers=[
           logging.FileHandler('/app/logs/service_name.log'),
           logging.StreamHandler()  # Keep console output
       ]
   )
   ```

3. **Update promtail-config.yaml** to include your service logs

## Commands

- `./logs.sh tail [service]` - Real-time log streaming
- `./logs.sh query [service]` - Recent log history
- `./logs.sh errors` - Error and warning logs only
- `./logs.sh stats` - Log statistics

## Supported Services

- web_bff
- auth
- db (all database services)

## Configuration

- **loki-config.yaml**: Loki server configuration
- **promtail-config.yaml**: Log collection and parsing rules
- **logs.sh**: Terminal log viewing utility

## Log Format

Services should use this format for consistent parsing:

```
2024-01-01 12:00:00,000 INFO:service_name:Log message here
```

## Troubleshooting

1. **No logs appearing?**

   - Check if service is writing to `/app/logs/`
   - Verify service has the shared volume mounted
   - Check promtail container logs: `docker logs ergolux_promtail`

2. **Can't connect to Loki?**

   - Ensure logging service is running: `docker-compose ps`
   - Check network connectivity: services must be on `service_network`

3. **Permission issues?**
   - Ensure log directory is writable: `chmod 755 /app/logs`
