#!/bin/sh
counter=0
while true; do 
  counter=$((counter + 1))
  if [ $((counter % 15)) -eq 0 ]; then 
    echo "$(date +'%Y-%m-%d %H:%M:%S') [WORKER] [ERROR] Failed to process job #$counter - Queue overflow" | tee -a /app/logs/worker.log
  elif [ $((counter % 8)) -eq 0 ]; then 
    echo "$(date +'%Y-%m-%d %H:%M:%S') [WORKER] [WARN] Job #$counter took longer than expected - Memory usage: 85%" | tee -a /app/logs/worker.log
  else 
    echo "$(date +'%Y-%m-%d %H:%M:%S') [WORKER] [INFO] Successfully processed background job #$counter - Queue size: 23" | tee -a /app/logs/worker.log
  fi
  sleep 3
done