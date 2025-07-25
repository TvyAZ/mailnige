#!/bin/bash
# Gmail Bot Monitoring Script - Production Version
# Runs every 5 minutes via cron to ensure bot stays healthy
# Cron: */5 * * * * /home/botuser/gmail-bot/monitor.sh

# Configuration
BOT_DIR="/home/botuser/gmail-bot"
LOG_FILE="$BOT_DIR/logs/monitor.log"
SERVICE_NAME="gmail-bot"
MAX_MEMORY_MB=400  # Maximum memory usage in MB
MAX_CPU_PERCENT=80  # Maximum CPU usage percentage
MAX_LOG_SIZE_MB=100  # Maximum log file size in MB

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ensure log directory exists
mkdir -p "$BOT_DIR/logs"

# Function to log messages with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to send alert (can be extended to send Telegram notifications)
send_alert() {
    log_message "🚨 ALERT: $1"
    echo -e "${RED}🚨 ALERT: $1${NC}"
    
    # Optional: Send to admin Telegram (uncomment and configure)
    # if [ -f "$BOT_DIR/config_production.py" ]; then
    #     BOT_TOKEN=$(python3 -c "import sys; sys.path.append('$BOT_DIR'); import config_production; print(config_production.BOT_TOKEN)" 2>/dev/null)
    #     ADMIN_ID=$(python3 -c "import sys; sys.path.append('$BOT_DIR'); import config_production; print(config_production.ADMIN_ID)" 2>/dev/null)
    #     if [ -n "$BOT_TOKEN" ] && [ -n "$ADMIN_ID" ]; then
    #         curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    #           -d chat_id="$ADMIN_ID" \
    #           -d text="🚨 Bot Monitor Alert: $1" >/dev/null 2>&1
    #     fi
    # fi
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log_message "✅ $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
    log_message "⚠️ $1"
}

# Check if bot service is running
check_service_status() {
    if ! systemctl is-active --quiet "$SERVICE_NAME"; then
        send_alert "Service $SERVICE_NAME is not running. Attempting to start..."
        
        if systemctl start "$SERVICE_NAME"; then
            print_success "Service $SERVICE_NAME started successfully"
            return 0
        else
            send_alert "Failed to start service $SERVICE_NAME"
            return 1
        fi
    else
        print_success "Service $SERVICE_NAME is running"
        return 0
    fi
}

# Check bot process health
check_process_health() {
    local pid=$(pgrep -f "python.*main.py" | head -1)
    
    if [ -z "$pid" ]; then
        send_alert "Bot process not found"
        return 1
    fi
    
    print_success "Bot process found (PID: $pid)"
    
    # Check memory usage
    local memory_kb=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ')
    if [ -n "$memory_kb" ]; then
        local memory_mb=$((memory_kb / 1024))
        
        if [ "$memory_mb" -gt "$MAX_MEMORY_MB" ]; then
            send_alert "High memory usage: ${memory_mb}MB (limit: ${MAX_MEMORY_MB}MB)"
            
            # Restart service due to high memory
            log_message "Restarting service due to high memory usage"
            systemctl restart "$SERVICE_NAME"
            return 0
        else
            print_success "Memory usage normal: ${memory_mb}MB"
        fi
    fi
    
    # Check CPU usage
    local cpu_percent=$(ps -o %cpu= -p "$pid" 2>/dev/null | tr -d ' ' | cut -d'.' -f1)
    if [ -n "$cpu_percent" ] && [ "$cpu_percent" -gt "$MAX_CPU_PERCENT" ]; then
        print_warning "High CPU usage: ${cpu_percent}%"
    else
        print_success "CPU usage normal: ${cpu_percent}%"
    fi
    
    return 0
}

# Check disk space
check_disk_space() {
    local disk_usage=$(df "$BOT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -gt 90 ]; then
        send_alert "Disk usage critical: ${disk_usage}%"
        
        # Clean up old logs and backups
        find "$BOT_DIR/logs" -name "*.log.*" -mtime +7 -delete 2>/dev/null
        find "$BOT_DIR/backups" -name "*.tar.gz" -mtime +7 -delete 2>/dev/null
        
        log_message "Cleaned up old files due to disk space"
    elif [ "$disk_usage" -gt 80 ]; then
        print_warning "Disk usage high: ${disk_usage}%"
    else
        print_success "Disk usage normal: ${disk_usage}%"
    fi
}

# Check log file sizes and rotate if necessary
check_log_sizes() {
    if [ -f "$BOT_DIR/bot.log" ]; then
        local log_size_mb=$(du -m "$BOT_DIR/bot.log" | cut -f1)
        
        if [ "$log_size_mb" -gt "$MAX_LOG_SIZE_MB" ]; then
            log_message "Bot log file too large: ${log_size_mb}MB, rotating..."
            
            # Rotate log file
            mv "$BOT_DIR/bot.log" "$BOT_DIR/logs/bot_$(date +%Y%m%d_%H%M%S).log"
            touch "$BOT_DIR/bot.log"
            chown botuser:botuser "$BOT_DIR/bot.log"
            
            print_success "Log file rotated successfully"
        else
            print_success "Log file size normal: ${log_size_mb}MB"
        fi
    fi
}

# Test bot API connectivity
check_bot_connectivity() {
    local config_file="$BOT_DIR/config_production.py"
    
    if [ -f "$config_file" ]; then
        # Extract bot token
        local bot_token=$(python3 -c "
import sys
sys.path.append('$BOT_DIR')
try:
    import config_production
    print(config_production.BOT_TOKEN)
except:
    print('')
" 2>/dev/null)
        
        if [ -n "$bot_token" ] && [ "$bot_token" != "your_bot_token_here" ]; then
            # Test if bot responds to getMe API call
            local response=$(timeout 10 curl -s "https://api.telegram.org/bot$bot_token/getMe" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('ok' if data.get('ok') else 'error')
except:
    print('error')
" 2>/dev/null)
            
            if [ "$response" = "ok" ]; then
                print_success "Bot API connectivity test passed"
                return 0
            else
                send_alert "Bot API connectivity test failed"
                return 1
            fi
        else
            print_warning "Bot token not configured properly"
            return 1
        fi
    else
        print_warning "Config file not found"
        return 1
    fi
}

# Check database integrity
check_database() {
    local db_file="$BOT_DIR/gmail_bot.db"
    
    if [ -f "$db_file" ]; then
        # Simple database integrity check
        if sqlite3 "$db_file" "PRAGMA integrity_check;" | grep -q "ok"; then
            print_success "Database integrity check passed"
            return 0
        else
            send_alert "Database integrity check failed"
            return 1
        fi
    else
        print_warning "Database file not found"
        return 1
    fi
}

# Main monitoring function
main() {
    echo -e "${BLUE}===========================================${NC}"
    echo -e "${BLUE}Gmail Bot Health Check - $(date)${NC}"
    echo -e "${BLUE}===========================================${NC}"
    
    log_message "Starting monitoring check"
    
    # Run all checks
    local checks_failed=0
    
    echo -e "\n${BLUE}🔍 Service Status Check${NC}"
    if ! check_service_status; then
        ((checks_failed++))
    fi
    
    echo -e "\n${BLUE}🖥️ Process Health Check${NC}"
    if ! check_process_health; then
        ((checks_failed++))
    fi
    
    echo -e "\n${BLUE}💾 Disk Space Check${NC}"
    check_disk_space
    
    echo -e "\n${BLUE}📝 Log Files Check${NC}"
    check_log_sizes
    
    echo -e "\n${BLUE}🌐 API Connectivity Check${NC}"
    if ! check_bot_connectivity; then
        ((checks_failed++))
    fi
    
    echo -e "\n${BLUE}🗄️ Database Check${NC}"
    if ! check_database; then
        ((checks_failed++))
    fi
    
    # Summary
    echo -e "\n${BLUE}===========================================${NC}"
    if [ "$checks_failed" -eq 0 ]; then
        print_success "All checks passed - bot is healthy"
    else
        send_alert "Monitoring completed with $checks_failed failed checks"
    fi
    echo -e "${BLUE}===========================================${NC}\n"
    
    # Cleanup old monitor logs (keep last 200 lines)
    if [ -f "$LOG_FILE" ]; then
        tail -200 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
}

# Check if running in quiet mode (for cron)
if [ "$1" = "--quiet" ]; then
    # Redirect output to log only
    main >> "$LOG_FILE" 2>&1
else
    # Interactive mode with colored output
    main
fi
