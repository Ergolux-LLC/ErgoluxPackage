#!/bin/bash

# Find terminal running SvelteKit dev server (if any)
PID=$(lsof -i:5173 -t 2>/dev/null)

if [ -n "$PID" ]; then
  echo "Found SvelteKit dev server running (PID: $PID)"
  echo "Stopping existing server..."
  kill $PID
  
  # Wait for the process to terminate
  while kill -0 $PID 2>/dev/null; do
    sleep 0.5
  done
  
  echo "Previous server stopped"
fi

# Start dev server
echo "Starting SvelteKit dev server..."
exec npm run dev:no-kill
