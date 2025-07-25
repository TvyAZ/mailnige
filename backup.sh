#!/bin/bash
# Gmail Bot Backup Script - Production Version
# Automated backup system for database, config, and logs
# Cron: 0 */6 * * * /home/botuser/gmail-bot/backup.sh --auto

# Configuration
BOT_DIR="/home/botuser/gmail-bot"
BACKUP_DIR="$BOT_DIR/backups"
REMOTE_BACKUP_DIR="/opt/backups/gmail-bot"  # System backup location
MAX_BACKUPS=10  # Keep last 10 backups locally
MAX_REMOTE_BACKUPS=30  # Keep last 30 backups remotely
RETENTION_DAYS=7  # Delete local backups older than 7 days

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Create backup directories
create_backup_dirs() {
    mkdir -p "$BACKUP_DIR"
    sudo mkdir -p "$REMOTE_BACKUP_DIR"
    sudo chown botuser:botuser "$REMOTE_BACKUP_DIR" 2>/dev/null || true
}

# Generate backup filename
get_backup_filename() {
    echo "gmail_bot_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
}

# Create database backup
backup_database() {
    local db_file="$BOT_DIR/gmail_bot.db"
    local backup_file="$1"
    
    if [ -f "$db_file" ]; then
        print_status "Backing up database..."
        
        # Create SQL dump as well for easier restoration
        sqlite3 "$db_file" .dump > "${backup_file%.tar.gz}_database.sql"
        
        # Copy database file
        cp "$db_file" "${backup_file%.tar.gz}_database.db"
        
        print_success "Database backup completed"
        return 0
    else
        print_warning "Database file not found: $db_file"
        return 1
    fi
}

# Create configuration backup
backup_config() {
    local backup_file="$1"
    
    print_status "Backing up configuration files..."
    
    # Copy config files (excluding sensitive data if needed)
    if [ -f "$BOT_DIR/config_production.py" ]; then
        cp "$BOT_DIR/config_production.py" "${backup_file%.tar.gz}_config.py"
    fi
    
    if [ -f "$BOT_DIR/bot_settings.json" ]; then
        cp "$BOT_DIR/bot_settings.json" "${backup_file%.tar.gz}_settings.json"
    fi
    
    # Note: credentials.json is excluded for security
    
    print_success "Configuration backup completed"
}

# Create logs backup
backup_logs() {
    local backup_file="$1"
    
    print_status "Backing up recent logs..."
    
    # Create logs backup directory
    local log_backup_dir="${backup_file%.tar.gz}_logs"
    mkdir -p "$log_backup_dir"
    
    # Copy recent log files (last 7 days)
    find "$BOT_DIR/logs" -name "*.log" -mtime -7 -exec cp {} "$log_backup_dir/" \; 2>/dev/null || true
    
    # Copy main bot log if exists
    if [ -f "$BOT_DIR/bot.log" ]; then
        cp "$BOT_DIR/bot.log" "$log_backup_dir/"
    fi
    
    print_success "Logs backup completed"
}

# Create main backup archive
create_backup_archive() {
    local backup_filename="$1"
    local backup_path="$BACKUP_DIR/$backup_filename"
    
    print_status "Creating backup archive: $backup_filename"
    
    # Create temporary backup directory
    local temp_dir="${backup_path%.tar.gz}_temp"
    mkdir -p "$temp_dir"
    
    # Backup database
    backup_database "$temp_dir/backup"
    
    # Backup configuration
    backup_config "$temp_dir/backup"
    
    # Backup logs
    backup_logs "$temp_dir/backup"
    
    # Create metadata file
    cat > "$temp_dir/backup_metadata.txt" << EOF
Gmail Bot Backup Metadata
========================
Backup Date: $(date)
Bot Directory: $BOT_DIR
Backup Type: Full
Bot Version: $(cd "$BOT_DIR" && git describe --tags 2>/dev/null || echo "unknown")
Git Commit: $(cd "$BOT_DIR" && git rev-parse HEAD 2>/dev/null || echo "unknown")
System Info: $(uname -a)
Python Version: $(python3 --version)
Disk Usage: $(df -h "$BOT_DIR" | tail -1)
Memory Usage: $(free -h | grep Mem)
EOF
    
    # Create compressed archive
    cd "$(dirname "$temp_dir")"
    tar -czf "$backup_path" -C "$temp_dir" .
    
    # Cleanup temporary files
    rm -rf "$temp_dir"
    
    if [ -f "$backup_path" ]; then
        local backup_size=$(du -h "$backup_path" | cut -f1)
        print_success "Backup created successfully: $backup_filename ($backup_size)"
        
        # Copy to remote backup location
        if [ -d "$REMOTE_BACKUP_DIR" ]; then
            cp "$backup_path" "$REMOTE_BACKUP_DIR/"
            print_success "Backup copied to remote location"
        fi
        
        return 0
    else
        print_error "Failed to create backup archive"
        return 1
    fi
}

# Clean old backups
cleanup_old_backups() {
    print_status "Cleaning up old backups..."
    
    # Clean local backups
    local backup_count=$(ls -1 "$BACKUP_DIR"/gmail_bot_backup_*.tar.gz 2>/dev/null | wc -l)
    
    if [ "$backup_count" -gt "$MAX_BACKUPS" ]; then
        local files_to_delete=$((backup_count - MAX_BACKUPS))
        print_status "Removing $files_to_delete old local backups..."
        
        ls -1t "$BACKUP_DIR"/gmail_bot_backup_*.tar.gz | tail -n "$files_to_delete" | xargs rm -f
    fi
    
    # Clean remote backups
    if [ -d "$REMOTE_BACKUP_DIR" ]; then
        local remote_count=$(ls -1 "$REMOTE_BACKUP_DIR"/gmail_bot_backup_*.tar.gz 2>/dev/null | wc -l)
        
        if [ "$remote_count" -gt "$MAX_REMOTE_BACKUPS" ]; then
            local remote_files_to_delete=$((remote_count - MAX_REMOTE_BACKUPS))
            print_status "Removing $remote_files_to_delete old remote backups..."
            
            ls -1t "$REMOTE_BACKUP_DIR"/gmail_bot_backup_*.tar.gz | tail -n "$remote_files_to_delete" | xargs rm -f
        fi
    fi
    
    # Clean backups older than retention period
    find "$BACKUP_DIR" -name "gmail_bot_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    print_success "Backup cleanup completed"
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    
    print_status "Verifying backup integrity..."
    
    if tar -tzf "$backup_file" >/dev/null 2>&1; then
        print_success "Backup integrity verified"
        return 0
    else
        print_error "Backup integrity check failed"
        return 1
    fi
}

# List available backups
list_backups() {
    echo -e "${BLUE}Available Backups:${NC}"
    echo "=================="
    
    if [ -d "$BACKUP_DIR" ]; then
        echo -e "${YELLOW}Local Backups:${NC}"
        ls -lh "$BACKUP_DIR"/gmail_bot_backup_*.tar.gz 2>/dev/null | awk '{print $9, $5, $6, $7, $8}' || echo "No local backups found"
        echo
    fi
    
    if [ -d "$REMOTE_BACKUP_DIR" ]; then
        echo -e "${YELLOW}Remote Backups:${NC}"
        ls -lh "$REMOTE_BACKUP_DIR"/gmail_bot_backup_*.tar.gz 2>/dev/null | awk '{print $9, $5, $6, $7, $8}' || echo "No remote backups found"
    fi
}

# Restore from backup
restore_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        return 1
    fi
    
    print_warning "This will restore the bot from backup and may overwrite current data!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping bot service..."
        systemctl stop gmail-bot 2>/dev/null || true
        
        print_status "Restoring from backup: $(basename "$backup_file")"
        
        # Create restore directory
        local restore_dir="/tmp/gmail_bot_restore_$$"
        mkdir -p "$restore_dir"
        
        # Extract backup
        tar -xzf "$backup_file" -C "$restore_dir"
        
        # Restore database
        if [ -f "$restore_dir/backup_database.db" ]; then
            cp "$restore_dir/backup_database.db" "$BOT_DIR/gmail_bot.db"
            chown botuser:botuser "$BOT_DIR/gmail_bot.db"
            print_success "Database restored"
        fi
        
        # Restore configuration
        if [ -f "$restore_dir/backup_config.py" ]; then
            cp "$restore_dir/backup_config.py" "$BOT_DIR/config_production.py"
            chown botuser:botuser "$BOT_DIR/config_production.py"
            print_success "Configuration restored"
        fi
        
        if [ -f "$restore_dir/backup_settings.json" ]; then
            cp "$restore_dir/backup_settings.json" "$BOT_DIR/bot_settings.json"
            chown botuser:botuser "$BOT_DIR/bot_settings.json"
            print_success "Settings restored"
        fi
        
        # Cleanup
        rm -rf "$restore_dir"
        
        print_status "Starting bot service..."
        systemctl start gmail-bot
        
        print_success "Restore completed successfully"
    else
        print_status "Restore cancelled"
    fi
}

# Show usage
show_usage() {
    echo "Gmail Bot Backup Script"
    echo "======================"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --auto              Run automated backup (for cron)"
    echo "  --create            Create a new backup interactively"
    echo "  --list              List available backups"
    echo "  --restore <file>    Restore from backup file"
    echo "  --verify <file>     Verify backup integrity"
    echo "  --cleanup           Clean old backups"
    echo "  --help              Show this help message"
    echo
    echo "Examples:"
    echo "  $0 --create                                    # Create backup"
    echo "  $0 --restore /path/to/backup.tar.gz          # Restore backup"
    echo "  $0 --auto                                     # Automated backup"
}

# Main function
main() {
    # Ensure we're running as botuser or root
    if [ "$USER" != "botuser" ] && [ "$USER" != "root" ]; then
        print_error "This script should be run as botuser or root"
        exit 1
    fi
    
    # Create backup directories
    create_backup_dirs
    
    case "${1:-}" in
        --auto)
            print_status "Running automated backup..."
            local backup_filename=$(get_backup_filename)
            if create_backup_archive "$backup_filename"; then
                verify_backup "$BACKUP_DIR/$backup_filename"
                cleanup_old_backups
                print_success "Automated backup completed successfully"
            else
                print_error "Automated backup failed"
                exit 1
            fi
            ;;
        --create)
            local backup_filename=$(get_backup_filename)
            if create_backup_archive "$backup_filename"; then
                verify_backup "$BACKUP_DIR/$backup_filename"
                print_success "Manual backup completed: $backup_filename"
            else
                print_error "Manual backup failed"
                exit 1
            fi
            ;;
        --list)
            list_backups
            ;;
        --restore)
            if [ -z "$2" ]; then
                print_error "Please specify backup file to restore"
                show_usage
                exit 1
            fi
            restore_backup "$2"
            ;;
        --verify)
            if [ -z "$2" ]; then
                print_error "Please specify backup file to verify"
                show_usage
                exit 1
            fi
            verify_backup "$2"
            ;;
        --cleanup)
            cleanup_old_backups
            ;;
        --help|*)
            show_usage
            ;;
    esac
}

# Run main function
main "$@"
