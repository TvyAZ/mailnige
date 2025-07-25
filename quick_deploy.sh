#!/bin/bash
# Gmail Bot Quick Deploy Script
# One-liner deployment for production VPS
# Usage: curl -sSL https://raw.githubusercontent.com/user/repo/main/quick_deploy.sh | sudo bash -s -- REPO_URL

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo
    echo -e "${BLUE}===========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===========================================${NC}"
}

# Get repository URL from argument
REPO_URL="${1:-https://github.com/your-username/mailnige.git}"

print_header "GMAIL BOT QUICK DEPLOY"
echo "Repository: $REPO_URL"
echo "Target: Production VPS Ubuntu"
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

# Validate repository URL
if [[ ! "$REPO_URL" =~ ^https://github\.com/.+/.+\.git$ ]]; then
    print_error "Invalid repository URL format!"
    print_status "Usage: curl -sSL https://raw.githubusercontent.com/user/repo/main/quick_deploy.sh | sudo bash -s -- REPO_URL"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt update >/dev/null 2>&1

# Install git if not present
if ! command -v git >/dev/null 2>&1; then
    print_status "Installing git..."
    apt install -y git >/dev/null 2>&1
fi

# Clone repository to temp directory
TEMP_DIR="/tmp/gmail-bot-deploy-$$"
print_status "Downloading deployment scripts..."
git clone "$REPO_URL" "$TEMP_DIR" >/dev/null 2>&1

# Check if production deploy script exists
if [ -f "$TEMP_DIR/production_deploy.sh" ]; then
    print_success "Production deployment script found"
    
    # Make executable and run
    chmod +x "$TEMP_DIR/production_deploy.sh"
    "$TEMP_DIR/production_deploy.sh" "$REPO_URL"
    
    # Cleanup
    rm -rf "$TEMP_DIR"
    
    print_success "Quick deployment completed!"
    print_status "Configure your bot: nano /home/botuser/gmail-bot/config_production.py"
    print_status "Start bot: gmail-bot start"
    
else
    print_error "Production deployment script not found in repository"
    rm -rf "$TEMP_DIR"
    exit 1
fi
