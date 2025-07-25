#!/bin/bash
# Gmail Bot System Health Check - Production Version
# Comprehensive health monitoring and diagnostics
# Usage: ./system_health_check_production.sh [--fix] [--verbose]

# Configuration
BOT_DIR="/home/botuser/gmail-bot"
SERVICE_NAME="gmail-bot"
CONFIG_FILE="$BOT_DIR/config_production.py"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Flags
FIX_ISSUES=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX_ISSUES=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Usage: $0 [--fix] [--verbose]"
            exit 1
            ;;
    esac
done

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Functions
print_header() {
    echo
    echo -e "${PURPLE}===========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${PURPLE}===========================================${NC}"
}

print_check() {
    ((TOTAL_CHECKS++))
    echo -e "${BLUE}[CHECK]${NC} $1"
}

print_pass() {
    ((PASSED_CHECKS++))
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    ((FAILED_CHECKS++))
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warn() {
    ((WARNING_CHECKS++))
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_info() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

print_fix() {
    echo -e "${CYAN}[FIX]${NC} $1"
}

# Check system requirements
check_system_requirements() {
    print_header "SYSTEM REQUIREMENTS CHECK"
    
    # Check Ubuntu version
    print_check "Checking Ubuntu version..."
    local ubuntu_version=$(lsb_release -rs 2>/dev/null)
    if [ -n "$ubuntu_version" ]; then
        local major_version=$(echo "$ubuntu_version" | cut -d'.' -f1)
        if [ "$major_version" -ge 20 ]; then
            print_pass "Ubuntu $ubuntu_version (supported)"
        else
            print_warn "Ubuntu $ubuntu_version (older version, consider upgrading)"
        fi
    else
        print_fail "Cannot detect Ubuntu version"
    fi
    
    # Check Python version
    print_check "Checking Python version..."
    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        local python_major=$(echo "$python_version" | cut -d'.' -f1)
        local python_minor=$(echo "$python_version" | cut -d'.' -f2)
        
        if [ "$python_major" -eq 3 ] && [ "$python_minor" -ge 8 ]; then
            print_pass "Python $python_version (supported)"
        else
            print_warn "Python $python_version (consider upgrading to 3.8+)"
        fi
    else
        print_fail "Python3 not found"
        if [ "$FIX_ISSUES" = true ]; then
            print_fix "Installing Python3..."
            sudo apt update && sudo apt install -y python3 python3-pip python3-venv
        fi
    fi
    
    # Check memory
    print_check "Checking available memory..."
    local total_mem=$(free -m | awk 'NR==2{print $2}')
    local available_mem=$(free -m | awk 'NR==2{print $7}')
    
    if [ "$total_mem" -ge 512 ]; then
        print_pass "Total memory: ${total_mem}MB (sufficient)"
    else
        print_warn "Total memory: ${total_mem}MB (low, consider upgrading)"
    fi
    
    if [ "$available_mem" -ge 256 ]; then
        print_pass "Available memory: ${available_mem}MB (good)"
    else
        print_warn "Available memory: ${available_mem}MB (low)"
    fi
    
    # Check disk space
    print_check "Checking disk space..."
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    local disk_available=$(df -h / | awk 'NR==2 {print $4}')
    
    if [ "$disk_usage" -lt 80 ]; then
        print_pass "Disk usage: ${disk_usage}% (available: $disk_available)"
    elif [ "$disk_usage" -lt 90 ]; then
        print_warn "Disk usage: ${disk_usage}% (available: $disk_available) - consider cleanup"
    else
        print_fail "Disk usage: ${disk_usage}% (available: $disk_available) - critical"
        if [ "$FIX_ISSUES" = true ]; then
            print_fix "Cleaning up old files..."
            find /var/log -name "*.log" -mtime +30 -delete 2>/dev/null || true
            apt autoremove -y 2>/dev/null || true
            apt autoclean 2>/dev/null || true
        fi
    fi
}

# Check bot installation
check_bot_installation() {
    print_header "BOT INSTALLATION CHECK"
    
    # Check bot directory
    print_check "Checking bot directory..."
    if [ -d "$BOT_DIR" ]; then
        print_pass "Bot directory exists: $BOT_DIR"
    else
        print_fail "Bot directory not found: $BOT_DIR"
        return 1
    fi
    
    # Check bot user
    print_check "Checking bot user..."
    if id "botuser" >/dev/null 2>&1; then
        print_pass "Bot user 'botuser' exists"
    else
        print_fail "Bot user 'botuser' not found"
        if [ "$FIX_ISSUES" = true ]; then
            print_fix "Creating bot user..."
            sudo adduser --disabled-password --gecos "" botuser
        fi
    fi
    
    # Check virtual environment
    print_check "Checking Python virtual environment..."
    if [ -d "$BOT_DIR/venv" ]; then
        print_pass "Virtual environment exists"
        
        # Check if venv is working
        if [ -f "$BOT_DIR/venv/bin/python" ]; then
            print_pass "Virtual environment Python executable found"
        else
            print_fail "Virtual environment Python executable missing"
        fi
    else
        print_fail "Virtual environment not found"
        if [ "$FIX_ISSUES" = true ]; then
            print_fix "Creating virtual environment..."
            sudo -u botuser python3 -m venv "$BOT_DIR/venv"
        fi
    fi
    
    # Check main bot file
    print_check "Checking main bot file..."
    if [ -f "$BOT_DIR/main.py" ]; then
        print_pass "main.py found"
    else
        print_fail "main.py not found"
    fi
    
    # Check requirements
    print_check "Checking requirements file..."
    if [ -f "$BOT_DIR/requirements.txt" ]; then
        print_pass "requirements.txt found"
        
        # Check if dependencies are installed
        if [ -f "$BOT_DIR/venv/bin/pip" ]; then
            local missing_deps=$("$BOT_DIR/venv/bin/pip" check 2>&1 | grep -c "No broken requirements found" || echo "0")
            if [ "$missing_deps" -eq 0 ]; then
                print_warn "Some Python dependencies may be missing or broken"
                if [ "$FIX_ISSUES" = true ]; then
                    print_fix "Installing/updating dependencies..."
                    sudo -u botuser bash -c "cd $BOT_DIR && source venv/bin/activate && pip install -r requirements.txt"
                fi
            else
                print_pass "Python dependencies check passed"
            fi
        fi
    else
        print_fail "requirements.txt not found"
    fi
}

# Check configuration
check_configuration() {
    print_header "CONFIGURATION CHECK"
    
    # Check config file
    print_check "Checking configuration file..."
    if [ -f "$CONFIG_FILE" ]; then
        print_pass "Configuration file exists"
        
        # Check if config can be imported
        if python3 -c "import sys; sys.path.append('$BOT_DIR'); import config_production" 2>/dev/null; then
            print_pass "Configuration file is valid Python"
            
            # Check bot token
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
                print_pass "Bot token is configured"
            else
                print_fail "Bot token is not configured properly"
            fi
            
            # Check admin ID
            local admin_id=$(python3 -c "
import sys
sys.path.append('$BOT_DIR')
try:
    import config_production
    print('configured' if hasattr(config_production, 'ADMIN_ID') and str(config_production.ADMIN_ID) != '123456789' else 'not_configured')
except:
    print('error')
" 2>/dev/null)
            
            if [ "$admin_id" = "configured" ]; then
                print_pass "Admin ID is configured"
            else
                print_fail "Admin ID is not configured properly"
            fi
            
        else
            print_fail "Configuration file has syntax errors"
        fi
    else
        print_fail "Configuration file not found: $CONFIG_FILE"
    fi
    
    # Check Google credentials
    print_check "Checking Google credentials..."
    if [ -f "$BOT_DIR/credentials.json" ]; then
        print_pass "Google credentials file exists"
        
        # Check if it's valid JSON
        if python3 -c "import json; json.load(open('$BOT_DIR/credentials.json'))" 2>/dev/null; then
            print_pass "Google credentials file is valid JSON"
        else
            print_fail "Google credentials file is not valid JSON"
        fi
    else
        print_fail "Google credentials file not found"
    fi
}

# Check service
check_service() {
    print_header "SERVICE CHECK"
    
    # Check systemd service file
    print_check "Checking systemd service file..."
    if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
        print_pass "Service file exists"
        
        # Check if service is enabled
        if systemctl is-enabled "$SERVICE_NAME" >/dev/null 2>&1; then
            print_pass "Service is enabled for auto-start"
        else
            print_warn "Service is not enabled for auto-start"
            if [ "$FIX_ISSUES" = true ]; then
                print_fix "Enabling service for auto-start..."
                # Check if running as root/sudo user
                if [ "$EUID" -eq 0 ] || groups | grep -q sudo; then
                    sudo systemctl enable "$SERVICE_NAME"
                else
                    print_info "Please run as root/sudo user to enable service:"
                    print_info "sudo systemctl enable $SERVICE_NAME"
                fi
            fi
        fi
    else
        print_fail "Service file not found"
    fi
    
    # Check service status
    print_check "Checking service status..."
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_pass "Service is running"
        
        # Check process details
        local pid=$(systemctl show "$SERVICE_NAME" --property=MainPID --value)
        if [ -n "$pid" ] && [ "$pid" != "0" ]; then
            local memory_mb=$(ps -o rss= -p "$pid" 2>/dev/null | awk '{print int($1/1024)}')
            local cpu_percent=$(ps -o %cpu= -p "$pid" 2>/dev/null | tr -d ' ')
            
            print_info "Process ID: $pid"
            print_info "Memory usage: ${memory_mb}MB"
            print_info "CPU usage: ${cpu_percent}%"
        fi
    else
        print_fail "Service is not running"
        
        if [ "$FIX_ISSUES" = true ]; then
            print_fix "Starting service..."
            # Check if running as root/sudo user
            if [ "$EUID" -eq 0 ] || groups | grep -q sudo; then
                sudo systemctl start "$SERVICE_NAME"
            else
                print_info "Please run as root/sudo user to start service:"
                print_info "sudo systemctl start $SERVICE_NAME"
                return
            fi
            sleep 3
            if systemctl is-active --quiet "$SERVICE_NAME"; then
                print_pass "Service started successfully"
            else
                print_fail "Failed to start service"
            fi
        fi
    fi
}

# Check network connectivity
check_network() {
    print_header "NETWORK CONNECTIVITY CHECK"
    
    # Check internet connectivity
    print_check "Checking internet connectivity..."
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        print_pass "Internet connectivity is working"
    else
        print_fail "No internet connectivity"
    fi
    
    # Check Telegram API connectivity
    print_check "Checking Telegram API connectivity..."
    if curl -s --connect-timeout 10 https://api.telegram.org >/dev/null; then
        print_pass "Telegram API is accessible"
    else
        print_fail "Cannot access Telegram API"
    fi
    
    # Check Google API connectivity
    print_check "Checking Google API connectivity..."
    if curl -s --connect-timeout 10 https://sheets.googleapis.com >/dev/null; then
        print_pass "Google Sheets API is accessible"
    else
        print_fail "Cannot access Google Sheets API"
    fi
}

# Generate summary report
generate_summary() {
    print_header "HEALTH CHECK SUMMARY"
    
    echo -e "Total checks: ${TOTAL_CHECKS}"
    echo -e "${GREEN}Passed: ${PASSED_CHECKS}${NC}"
    echo -e "${YELLOW}Warnings: ${WARNING_CHECKS}${NC}"
    echo -e "${RED}Failed: ${FAILED_CHECKS}${NC}"
    echo
    
    local success_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    
    if [ "$FAILED_CHECKS" -eq 0 ]; then
        if [ "$WARNING_CHECKS" -eq 0 ]; then
            echo -e "${GREEN}🎉 All checks passed! Bot is in excellent health.${NC}"
        else
            echo -e "${YELLOW}⚠️ Bot is healthy with minor warnings.${NC}"
        fi
    else
        echo -e "${RED}❌ Bot has critical issues that need attention.${NC}"
        echo -e "${YELLOW}💡 Run with --fix flag to attempt automatic fixes.${NC}"
    fi
    
    echo -e "\nHealth Score: ${success_rate}%"
    
    if [ "$success_rate" -ge 90 ]; then
        echo -e "${GREEN}Status: EXCELLENT${NC}"
    elif [ "$success_rate" -ge 80 ]; then
        echo -e "${YELLOW}Status: GOOD${NC}"
    elif [ "$success_rate" -ge 70 ]; then
        echo -e "${YELLOW}Status: FAIR${NC}"
    else
        echo -e "${RED}Status: POOR${NC}"
    fi
}

# Main execution
main() {
    print_header "GMAIL BOT SYSTEM HEALTH CHECK"
    echo -e "Timestamp: $(date)"
    echo -e "Hostname: $(hostname)"
    echo -e "Fix mode: $([ "$FIX_ISSUES" = true ] && echo "ENABLED" || echo "DISABLED")"
    echo -e "Verbose mode: $([ "$VERBOSE" = true ] && echo "ENABLED" || echo "DISABLED")"
    
    # Run all checks
    check_system_requirements
    check_bot_installation
    check_configuration
    check_service
    check_network
    
    # Generate summary
    generate_summary
    
    # Exit with appropriate code
    if [ "$FAILED_CHECKS" -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main
