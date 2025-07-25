#!/bin/bash
# Gmail Bot Health Check Wrapper
# Tự động detect user và chạy health check với quyền phù hợp

BOT_DIR="/home/botuser/gmail-bot"
HEALTH_CHECK_SCRIPT="$BOT_DIR/system_health_check.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
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

# Check if script exists
if [ ! -f "$HEALTH_CHECK_SCRIPT" ]; then
    print_error "Health check script not found: $HEALTH_CHECK_SCRIPT"
    exit 1
fi

# Check current user and permissions
CURRENT_USER=$(whoami)
print_info "Current user: $CURRENT_USER"

if [ "$CURRENT_USER" = "root" ]; then
    print_info "Running as root - all checks and fixes available"
    "$HEALTH_CHECK_SCRIPT" "$@"
elif groups | grep -q sudo; then
    print_info "User has sudo privileges - all checks and fixes available"
    "$HEALTH_CHECK_SCRIPT" "$@"
elif [ "$CURRENT_USER" = "botuser" ]; then
    print_warning "Running as botuser - limited fixes available"
    print_info "For service management, use: sudo -u root $0 $*"
    "$HEALTH_CHECK_SCRIPT" "$@"
else
    print_warning "Limited user - some checks may fail"
    print_info "For full functionality, run as: sudo $0 $*"
    "$HEALTH_CHECK_SCRIPT" "$@"
fi
