
#!/bin/bash
set -e

host="$DB_HOST"
port="$DB_PORT"
user="$DB_USER"
dbname="$DB_NAME"
max_retries=60
retry=0

echo "Waiting for Postgres to be available at $host:$port..."
until PGPASSWORD="$DB_PASS" psql -h "$host" -U "$user" -d "$dbname" -p "$port" -c '\q' 2>/dev/null; do
  retry=$((retry+1))
  if [ $retry -ge $max_retries ]; then
    echo "Error: Could not connect to Postgres at $host:$port after $max_retries attempts."
    exit 1
  fi
  echo "Postgres is unavailable - sleeping ($retry/$max_retries)"
  sleep 1
done

echo "Postgres is up - continuing"
exec "$@"
