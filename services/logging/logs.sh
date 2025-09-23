#!/bin/bash

# Enhanced logcli wrapper for Ergolux services
# Usage: ./logs.sh [tail|query] [service]

LOKI_URL="http://localhost:3100"

print_usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  tail [service]     - Tail logs in real-time (service: web_bff, account_setup, auth, db, or all)"
    echo "  query [service]    - Show recent logs (service: web_bff, account_setup, auth, db, or all)"
    echo "  errors             - Show only error/warning logs"
    echo "  stats              - Show log statistics"
    echo ""
    echo "Examples:"
    echo "  $0 tail            - Tail all services"
    echo "  $0 tail web_bff    - Tail only web_bff service"
    echo "  $0 query account_setup - Show recent account_setup logs"
    echo "  $0 errors          - Show error logs only"
}

format_output() {
    while IFS= read -r line; do
        if [[ $line == *"{filename="* ]]; then
            # Extract timestamp and message
            timestamp=$(echo "$line" | grep -o '^[0-9-]*T[0-9:.-]*')
            
            if [[ $line == *"web-bff-service"* ]]; then
                service_color="\033[32m[WEB_BFF]\033[0m"
            elif [[ $line == *"account-setup-service"* ]]; then
                service_color="\033[36m[ACCOUNT_SETUP]\033[0m"
            elif [[ $line == *"auth-service"* ]]; then
                service_color="\033[34m[AUTH]\033[0m"
            elif [[ $line == *"db-services"* ]]; then
                service_color="\033[35m[DB]\033[0m"
            else
                service_color="\033[37m[UNKNOWN]\033[0m"
            fi
            
            # Extract log level and add colors
            if [[ $line == *"ERROR"* ]]; then
                level_color="\033[31mERROR\033[0m"
            elif [[ $line == *"WARN"* ]]; then
                level_color="\033[33mWARN\033[0m"
            elif [[ $line == *"INFO"* ]]; then
                level_color="\033[37mINFO\033[0m"
            elif [[ $line == *"DEBUG"* ]]; then
                level_color="\033[90mDEBUG\033[0m"
            else
                level_color="INFO"
            fi
            
            # Extract message part
            message=$(echo "$line" | sed 's/.*message="\([^"]*\)".*/\1/')
            
            # Format timestamp
            formatted_time=$(echo "$timestamp" | cut -d'T' -f2 | cut -d'.' -f1)
            
            echo -e "${formatted_time} ${service_color} ${level_color} ${message}"
        else
            echo "$line"
        fi
    done
}

case "$1" in
    "tail")
        if [ -n "$2" ]; then
            service="$2"
            case "$service" in
                "web_bff")
                    query='{service="web_bff"}'
                    ;;
                "account_setup")
                    query='{service="account_setup"}'
                    ;;
                "auth")
                    query='{service="auth"}'
                    ;;
                "db")
                    query='{service="db"}'
                    ;;
                *)
                    echo "Unknown service: $service"
                    print_usage
                    exit 1
                    ;;
            esac
        else
            query='{job=~".+"}'
        fi
        
        echo "🔄 Tailing logs for service: ${2:-all services}"
        echo "Press Ctrl+C to stop"
        echo "---"
        
        docker run --rm --network=service_network \
            grafana/logcli:latest \
            --addr="http://ergolux_loki:3100" \
            query --tail --follow "$query" | format_output
        ;;
        
    "query")
        if [ -n "$2" ]; then
            service="$2"
            case "$service" in
                "web_bff")
                    query='{service="web_bff"}'
                    ;;
                "account_setup")
                    query='{service="account_setup"}'
                    ;;
                "auth")
                    query='{service="auth"}'
                    ;;
                "db")
                    query='{service="db"}'
                    ;;
                *)
                    echo "Unknown service: $service"
                    print_usage
                    exit 1
                    ;;
            esac
        else
            query='{job=~".+"}'
        fi
        
        echo "📋 Recent logs for service: ${2:-all services}"
        echo "---"
        
        docker run --rm --network=service_network \
            grafana/logcli:latest \
            --addr="http://ergolux_loki:3100" \
            query --limit=50 "$query" | format_output
        ;;
        
    "errors")
        echo "🚨 Error and warning logs from all services"
        echo "---"
        
        docker run --rm --network=service_network \
            grafana/logcli:latest \
            --addr="http://ergolux_loki:3100" \
            query --limit=50 '{level=~"ERROR|WARN"}' | format_output
        ;;
        
    "stats")
        echo "📊 Log statistics"
        echo "---"
        
        docker run --rm --network=service_network \
            grafana/logcli:latest \
            --addr="http://ergolux_loki:3100" \
            stats '{job=~".+"}' --since=1h
        ;;
        
    "")
        print_usage
        ;;
        
    *)
        echo "Unknown command: $1"
        print_usage
        exit 1
        ;;
esac