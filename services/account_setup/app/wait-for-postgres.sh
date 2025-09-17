#!/bin/bash
set -e

host="$POSTGRES_HOST"
shift

done
until pg_isready -h "$host" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "Waiting for postgres at $host:$POSTGRES_PORT..."
  sleep 1
done

exec python /app/main.py
