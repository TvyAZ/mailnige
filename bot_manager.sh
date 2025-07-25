#!/bin/bash
# Gmail Bot Manager - Production Management Script
# Comprehensive bot management tool for production VPS
# Usage: gmail-bot [command] [options]

# Configuration
BOT_DIR="/home/botuser/gmail-bot"
SERVICE_NAME="gmail-bot"
CONFIG_FILE="$BOT_DIR/config_production.py"
LOG_FILE="$BOT_DIR/bot.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo
    echo -e "${PURPLE}===========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${PURPLE}===========================================${NC}"
}

# Check if we're in the right directory and user
check_environment() {
    if [ ! -d "$BOT_DIR" ]; then
        print_error "Bot directory not found: $BOT_DIR"
        exit 1
    fi
    
    # Try to switch to botuser if running as root
    if [ "$USER" = "root" ]; then
        exec sudo -u botuser "$0" "$@"
    elif [ "$USER" != "botuser" ]; then
        print_error "This script should be run as botuser"
        exit 1
    fi
}

# Start bot service
start_bot() {
    print_header "STARTING GMAIL BOT"
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_warning "Bot is already running"
        show_status
        return 0
    fi
    
    print_status "Starting bot service..."
    
    if sudo systemctl start "$SERVICE_NAME"; then
        sleep 3
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            print_success "Bot started successfully"
            show_status
        else
            print_error "Bot failed to start properly"
            show_logs --tail 20
            return 1
        fi
    else
        print_error "Failed to start bot service"
        return 1
    fi
}

# Stop bot service
stop_bot() {
    print_header "STOPPING GMAIL BOT"
    
    if ! systemctl is-active --quiet "$SERVICE_NAME"; then
        print_warning "Bot is not running"
        return 0
    fi
    
    print_status "Stopping bot service..."
    
    if sudo systemctl stop "$SERVICE_NAME"; then
        sleep 2
        print_success "Bot stopped successfully"
    else
        print_error "Failed to stop bot service"
        return 1
    fi
}

# Restart bot service
restart_bot() {
    print_header "RESTARTING GMAIL BOT"
    
    print_status "Restarting bot service..."
    
    if sudo systemctl restart "$SERVICE_NAME"; then
        sleep 3
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            print_success "Bot restarted successfully"
            show_status
        else
            print_error "Bot failed to restart properly"
            show_logs --tail 20
            return 1
        fi
    else
        print_error "Failed to restart bot service"
        return 1
    fi
}

# Show bot status
show_status() {
    print_header "GMAIL BOT STATUS"
    
    # Service status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Service Status: RUNNING ✅"
    else
        print_error "Service Status: STOPPED ❌"
    fi
    
    # Process information
    local pid=$(pgrep -f "python.*main.py" | head -1)
    if [ -n "$pid" ]; then
        print_success "Process ID: $pid"
        
        # Memory usage
        local memory_kb=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ')
        if [ -n "$memory_kb" ]; then
            local memory_mb=$((memory_kb / 1024))
            print_status "Memory Usage: ${memory_mb}MB"
        fi
        
        # CPU usage
        local cpu_percent=$(ps -o %cpu= -p "$pid" 2>/dev/null | tr -d ' ')
        if [ -n "$cpu_percent" ]; then
            print_status "CPU Usage: ${cpu_percent}%"
        fi
        
        # Process uptime
        local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null)
        if [ -n "$start_time" ]; then
            print_status "Started: $start_time"
        fi
    else
        print_warning "Bot process not found"
    fi
    
    # Check configuration
    if [ -f "$CONFIG_FILE" ]; then
        print_success "Configuration: Available"
        
        # Check bot token (without revealing it)
        local bot_token=$(python3 -c "
import sys
sys.path.append('$BOT_DIR')
try:
    import config_production
    print('configured' if config_production.BOT_TOKEN and config_production.BOT_TOKEN != 'your_bot_token_here' else 'not_configured')
except:
    print('error')
" 2>/dev/null)
        
        if [ "$bot_token" = "configured" ]; then
            print_success "Bot Token: Configured ✅"
        else
            print_error "Bot Token: Not configured ❌"
        fi
    else
        print_error "Configuration: Missing ❌"
    fi
    
    # Database status
    if [ -f "$BOT_DIR/gmail_bot.db" ]; then
        print_success "Database: Available"
        
        # Database size
        local db_size=$(du -h "$BOT_DIR/gmail_bot.db" | cut -f1)
        print_status "Database Size: $db_size"
    else
        print_warning "Database: Not found"
    fi
    
    # Disk usage
    local disk_usage=$(df "$BOT_DIR" | awk 'NR==2 {print $5}')
    print_status "Disk Usage: $disk_usage"
    
    # Last backup
    local last_backup=$(ls -t "$BOT_DIR/backups"/gmail_bot_backup_*.tar.gz 2>/dev/null | head -1)
    if [ -n "$last_backup" ]; then
        local backup_date=$(stat -c %y "$last_backup" | cut -d' ' -f1,2)
        print_success "Last Backup: $backup_date"
    else
        print_warning "No backups found"
    fi
    
    echo
}

# Show logs
show_logs() {
    local lines=50
    local follow=false
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --tail)
                lines="$2"
                shift 2
                ;;
            -f|--follow)
                follow=true
                shift
                ;;
            *)
                break
                ;;
        esac
    done
    
    print_header "GMAIL BOT LOGS"
    
    if [ "$follow" = true ]; then
        print_status "Following logs (Ctrl+C to stop)..."
        echo
        
        # Follow both bot log and systemd journal
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE" &
            local tail_pid=$!
        fi
        
        journalctl -u "$SERVICE_NAME" -f &
        local journal_pid=$!
        
        # Cleanup on exit
        trap "kill $tail_pid $journal_pid 2>/dev/null" EXIT
        wait
    else
        # Show recent logs
        if [ -f "$LOG_FILE" ]; then
            print_status "Bot Application Logs (last $lines lines):"
            echo
            tail -n "$lines" "$LOG_FILE"
            echo
        fi
        
        print_status "System Service Logs (last $lines lines):"
        echo
        journalctl -u "$SERVICE_NAME" --no-pager -n "$lines"
    fi
}

# Update bot from repository
update_bot() {
    print_header "UPDATING GMAIL BOT"
    
    # Check if we're in a git repository
    cd "$BOT_DIR"
    if [ ! -d ".git" ]; then
        print_error "Not a git repository. Cannot update."
        return 1
    fi
    
    # Stop bot before update
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "Stopping bot for update..."
        sudo systemctl stop "$SERVICE_NAME"
    fi
    
    # Backup current version
    print_status "Creating backup before update..."
    "$BOT_DIR/backup.sh" --create
    
    # Update from repository
    print_status "Fetching latest changes..."
    if git fetch origin; then
        print_success "Fetched latest changes"
    else
        print_error "Failed to fetch changes"
        return 1
    fi
    
    # Show changes that will be applied
    local current_commit=$(git rev-parse HEAD)
    local latest_commit=$(git rev-parse origin/main)
    
    if [ "$current_commit" = "$latest_commit" ]; then
        print_success "Already up to date"
        sudo systemctl start "$SERVICE_NAME"
        return 0
    fi
    
    print_status "Changes to be applied:"
    git log --oneline "$current_commit..$latest_commit"
    echo
    
    # Apply update
    print_status "Applying update..."
    if git merge origin/main; then
        print_success "Code updated successfully"
    else
        print_error "Failed to merge changes"
        return 1
    fi
    
    # Update dependencies if requirements changed
    if git diff --name-only "$current_commit..$latest_commit" | grep -q requirements; then
        print_status "Updating Python dependencies..."
        source venv/bin/activate
        pip install -r requirements.txt
    fi
    
    # Restart bot
    print_status "Starting updated bot..."
    sudo systemctl start "$SERVICE_NAME"
    
    sleep 3
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Bot updated and restarted successfully"
        print_status "New version: $(git rev-parse --short HEAD)"
    else
        print_error "Bot failed to start after update"
        print_warning "Consider restoring from backup"
        return 1
    fi
}

# Run health check
health_check() {
    print_header "GMAIL BOT HEALTH CHECK"
    
    # Run comprehensive health check
    if [ -f "$BOT_DIR/monitor.sh" ]; then
        "$BOT_DIR/monitor.sh"
    else
        print_warning "Health check script not found, running basic checks..."
        show_status
    fi
}

# Create backup
create_backup() {
    print_header "CREATING BACKUP"
    
    if [ -f "$BOT_DIR/backup.sh" ]; then
        "$BOT_DIR/backup.sh" --create
    else
        print_error "Backup script not found"
        return 1
    fi
}

# Clean up logs and temporary files
cleanup() {
    print_header "CLEANING UP"
    
    print_status "Cleaning old log files..."
    
    # Clean old rotated logs (older than 7 days)
    find "$BOT_DIR/logs" -name "*.log.*" -mtime +7 -delete 2>/dev/null || true
    
    # Clean old backups (keep last 5)
    local backup_count=$(ls -1 "$BOT_DIR/backups"/gmail_bot_backup_*.tar.gz 2>/dev/null | wc -l)
    if [ "$backup_count" -gt 5 ]; then
        local files_to_delete=$((backup_count - 5))
        print_status "Removing $files_to_delete old backups..."
        ls -1t "$BOT_DIR/backups"/gmail_bot_backup_*.tar.gz | tail -n "$files_to_delete" | xargs rm -f
    fi
    
    # Clean Python cache
    find "$BOT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BOT_DIR" -name "*.pyc" -delete 2>/dev/null || true
    
    # Clean temporary files
    rm -rf "$BOT_DIR/temp/*" 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Show configuration
show_config() {
    print_header "GMAIL BOT CONFIGURATION"
    
    if [ -f "$CONFIG_FILE" ]; then
        print_status "Configuration file: $CONFIG_FILE"
        echo
        
        # Show configuration (mask sensitive data)
        python3 -c "
import sys
sys.path.append('$BOT_DIR')
try:
    import config_production as config
    print('Bot Configuration:')
    print('================')
    
    # Safe attributes to show
    safe_attrs = ['DEFAULT_GMAIL_PRICE', 'MIN_DEPOSIT', 'MAX_DEPOSIT', 'LOG_LEVEL', 'MAX_WORKERS']
    
    for attr in safe_attrs:
        if hasattr(config, attr):
            print(f'{attr}: {getattr(config, attr)}')
    
    # Show masked sensitive data
    if hasattr(config, 'BOT_TOKEN'):
        token = getattr(config, 'BOT_TOKEN')
        if token and token != 'your_bot_token_here':
            print(f'BOT_TOKEN: {token[:10]}...{token[-5:]} (masked)')
        else:
            print('BOT_TOKEN: Not configured')
    
    if hasattr(config, 'ADMIN_ID'):
        admin_id = getattr(config, 'ADMIN_ID')
        if admin_id and str(admin_id) != '123456789':
            print(f'ADMIN_ID: {admin_id}')
        else:
            print('ADMIN_ID: Not configured')
            
    print()
    print('Database:', 'gmail_bot.db' if hasattr(config, 'DATABASE_URL') else 'Not configured')
    print('Google Sheets:', 'Configured' if hasattr(config, 'GOOGLE_SHEETS_ID') else 'Not configured')
    
except Exception as e:
    print(f'Error reading configuration: {e}')
"
    else
        print_error "Configuration file not found: $CONFIG_FILE"
    fi
}

# Show usage help
show_help() {
    echo -e "${CYAN}Gmail Bot Manager - Production Management Tool${NC}"
    echo "=============================================="
    echo
    echo "Usage: gmail-bot [COMMAND] [OPTIONS]"
    echo
    echo -e "${YELLOW}Commands:${NC}"
    echo "  start              Start the bot service"
    echo "  stop               Stop the bot service"
    echo "  restart            Restart the bot service"
    echo "  status             Show bot status and information"
    echo "  logs [OPTIONS]     Show bot logs"
    echo "  update             Update bot from git repository"
    echo "  backup             Create a backup"
    echo "  health             Run comprehensive health check"
    echo "  cleanup            Clean up old logs and files"
    echo "  config             Show current configuration"
    echo "  help               Show this help message"
    echo
    echo -e "${YELLOW}Log Options:${NC}"
    echo "  --tail N           Show last N lines (default: 50)"
    echo "  -f, --follow       Follow logs in real-time"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo "  gmail-bot start                    # Start the bot"
    echo "  gmail-bot logs --tail 100         # Show last 100 log lines"
    echo "  gmail-bot logs -f                 # Follow logs in real-time"
    echo "  gmail-bot update                  # Update from repository"
    echo "  gmail-bot health                  # Run health check"
    echo
}

# Main function
main() {
    # Check environment
    check_environment
    
    # Parse command
    case "${1:-help}" in
        start)
            start_bot
            ;;
        stop)
            stop_bot
            ;;
        restart)
            restart_bot
            ;;
        status)
            show_status
            ;;
        logs)
            shift
            show_logs "$@"
            ;;
        update)
            update_bot
            ;;
        backup)
            create_backup
            ;;
        health)
            health_check
            ;;
        cleanup)
            cleanup
            ;;
        config)
            show_config
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
