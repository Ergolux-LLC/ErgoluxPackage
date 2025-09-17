#!/bin/bash

# Enhanced logcli wrapper for developers
# Usage: ./logcli-dev.sh [tail|query] [service]

LOKI_URL="http://localhost:3100"

print_usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  tail [service]     - Tail logs in real-time (service: web, worker, or all)"
    echo "  query [service]    - Show recent logs (service: web, worker, or all)"
    echo "  errors             - Show only error/warning logs"
    echo "  stats              - Show log statistics"
    echo ""
    echo "Examples:"
    echo "  $0 tail            - Tail all services"
    echo "  $0 tail web        - Tail only web service"
    echo "  $0 query worker    - Show recent worker logs"
    echo "  $0 errors          - Show error logs only"
}

format_output() {
    while IFS= read -r line; do
        if [[ $line == *"{filename="* ]]; then
            # Extract timestamp and message
            timestamp=$(echo "$line" | grep -o '^[0-9-]*T[0-9:.-]*')
            
            if [[ $line == *"web-service"* ]]; then
                echo -e "\033[32m$timestamp [WEB]\033[0m ${line##*'} '}"
            elif [[ $line == *"worker-service"* ]]; then
                echo -e "\033[34m$timestamp [WORKER]\033[0m ${line##*'} '}"
            else
                echo "$line"
            fi
        else
            echo "$line"
        fi
    done
}

case "$1" in
    "tail")
        if [ "$2" = "web" ]; then
            echo "🔄 Tailing WEB service logs..."
            logcli query '{job="web-service"}' --tail --addr="$LOKI_URL" | format_output
        elif [ "$2" = "worker" ]; then
            echo "🔄 Tailing WORKER service logs..."
            logcli query '{job="worker-service"}' --tail --addr="$LOKI_URL" | format_output
        else
            echo "🔄 Tailing ALL service logs..."
            logcli query '{job=~"web-service|worker-service"}' --tail --addr="$LOKI_URL" | format_output
        fi
        ;;
    "query")
        if [ "$2" = "web" ]; then
            echo "📋 Recent WEB service logs:"
            logcli query '{job="web-service"}' --limit=20 --addr="$LOKI_URL" | format_output
        elif [ "$2" = "worker" ]; then
            echo "📋 Recent WORKER service logs:"
            logcli query '{job="worker-service"}' --limit=20 --addr="$LOKI_URL" | format_output
        else
            echo "📋 Recent logs from ALL services:"
            logcli query '{job=~"web-service|worker-service"}' --limit=30 --addr="$LOKI_URL" | format_output
        fi
        ;;
    "errors")
        echo "❌ Searching for error/warning logs..."
        logcli query '{job=~"web-service|worker-service"} |~ "(?i)(error|warn|fail|exception)"' --limit=50 --addr="$LOKI_URL" | format_output
        ;;
    "stats")
        echo "📊 Log Statistics:"
        echo ""
        echo "Web Service Logs (last hour):"
        web_count=$(logcli query '{job="web-service"}' --since=1h --limit=1000 --addr="$LOKI_URL" --quiet | wc -l 2>/dev/null)
        echo "  Count: $web_count"
        
        echo ""
        echo "Worker Service Logs (last hour):"
        worker_count=$(logcli query '{job="worker-service"}' --since=1h --limit=1000 --addr="$LOKI_URL" --quiet | wc -l 2>/dev/null)
        echo "  Count: $worker_count"
        
        echo ""
        echo "Total: $((web_count + worker_count)) log entries"
        ;;
    "help"|"-h"|"--help")
        print_usage
        ;;
    *)
        echo "❌ Invalid command: $1"
        echo ""
        print_usage
        exit 1
        ;;
esac