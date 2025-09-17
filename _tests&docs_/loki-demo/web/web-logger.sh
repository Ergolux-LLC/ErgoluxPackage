#!/bin/sh
counter=0
while true; do 
  counter=$((counter + 1))
  if [ $((counter % 10)) -eq 0 ]; then 
    echo "$(date +'%Y-%m-%d %H:%M:%S') [WEB] [ERROR] Database connection failed - Request #$counter" | tee -a /app/logs/web.log
  elif [ $((counter % 7)) -eq 0 ]; then 
    echo "$(date +'%Y-%m-%d %H:%M:%S') [WEB] [WARN] High response time detected - Request #$counter took 1200ms" | tee -a /app/logs/web.log
  else 
    echo "$(date +'%Y-%m-%d %H:%M:%S') [WEB] [INFO] Processing web request #$counter - Response: 200 OK" | tee -a /app/logs/web.log
  fi
  sleep 2
done