#!/bin/bash
# Production VPS Deployment Script for Gmail Bot
# Usage: bash production_deploy.sh [REPO_URL]
# Example: bash production_deploy.sh https://github.com/username/mailnige.git

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Configuration
BOT_USER="botuser"
BOT_DIR="/home/$BOT_USER/gmail-bot"
SERVICE_NAME="gmail-bot"
REPO_URL="${1:-https://github.com/your-username/mailnige.git}"

# Validate repository URL
if [[ ! "$REPO_URL" =~ ^https://github\.com/.+/.+\.git$ ]]; then
    print_error "Invalid repository URL format!"
    print_status "Usage: bash production_deploy.sh https://github.com/username/repo.git"
    exit 1
fi

print_header "GMAIL BOT - PRODUCTION VPS DEPLOYMENT"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

# STEP 1: Update system and install dependencies
print_header "STEP 1: SYSTEM PREPARATION"
print_status "Updating system packages..."
apt update && apt upgrade -y

print_status "Installing required packages..."
apt install -y python3 python3-pip python3-venv git curl wget nano ufw \
               fail2ban supervisor nginx htop tree unzip sqlite3 \
               logrotate rsync cron

print_success "System packages installed successfully"

# STEP 2: Create bot user
print_header "STEP 2: USER SETUP"
if id "$BOT_USER" &>/dev/null; then
    print_warning "User $BOT_USER already exists"
else
    print_status "Creating user $BOT_USER..."
    adduser --disabled-password --gecos "" $BOT_USER
    usermod -aG sudo $BOT_USER
    print_success "User $BOT_USER created successfully"
fi

# STEP 3: Setup project directory
print_header "STEP 3: PROJECT SETUP"
print_status "Setting up project directory..."

if [ -d "$BOT_DIR" ]; then
    print_warning "Bot directory already exists. Creating backup..."
    mv "$BOT_DIR" "${BOT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi

# Clone repository as botuser
sudo -u $BOT_USER git clone "$REPO_URL" "$BOT_DIR"
cd "$BOT_DIR"

# Create virtual environment
print_status "Creating Python virtual environment..."
sudo -u $BOT_USER python3 -m venv venv
sudo -u $BOT_USER bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u $BOT_USER bash -c "source venv/bin/activate && pip install -r requirements.txt"

print_success "Virtual environment created and dependencies installed"

# Create necessary directories
print_status "Creating necessary directories..."
sudo -u $BOT_USER mkdir -p "$BOT_DIR/logs"
sudo -u $BOT_USER mkdir -p "$BOT_DIR/backups"
sudo -u $BOT_USER mkdir -p "$BOT_DIR/temp"

# Set permissions
chown -R $BOT_USER:$BOT_USER "$BOT_DIR"
chmod +x "$BOT_DIR"/*.sh 2>/dev/null || true

print_success "Project setup completed"

# STEP 4: Create configuration template
print_header "STEP 4: CONFIGURATION SETUP"
print_status "Creating configuration template..."

cat > "$BOT_DIR/config_production.py" << 'EOF'
# ===========================================
# GMAIL BOT TELEGRAM - PRODUCTION CONFIG
# ===========================================

# Bot Configuration
BOT_TOKEN = "your_bot_token_here"  # Bot token từ @BotFather
ADMIN_ID = 123456789  # Telegram ID của admin

# Database
DATABASE_URL = "gmail_bot.db"  # SQLite database file

# Google Sheets Configuration
GOOGLE_SHEETS_ID = "your_google_sheets_id_here"
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# Business Settings
DEFAULT_GMAIL_PRICE = 50000  # Giá mặc định (VND)
MIN_DEPOSIT = 50000  # Số tiền nạp tối thiểu
MAX_DEPOSIT = 10000000  # Số tiền nạp tối đa

# Bank Information (for user deposits)
BANK_INFO = {
    "bank_name": "Vietcombank",
    "account_number": "1234567890",
    "account_name": "NGUYEN VAN A",
    "content": "NAPBOT {user_id}"  # Template nội dung chuyển khoản
}

# System Settings
WEBHOOK_MODE = False  # Set True nếu dùng webhook với Nginx
WEBHOOK_URL = ""  # URL webhook nếu dùng
WEBHOOK_PORT = 8443  # Port webhook

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
MAX_WORKERS = 10  # Số thread xử lý tối đa

# Rate Limiting
RATE_LIMIT_MESSAGES = 30  # Số tin nhắn tối đa trong window
RATE_LIMIT_WINDOW = 60  # Thời gian window (giây)

# Auto-backup settings
BACKUP_ENABLED = True
BACKUP_INTERVAL_HOURS = 6  # Backup mỗi 6 giờ
BACKUP_KEEP_DAYS = 7  # Giữ backup trong 7 ngày

# Security
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
EOF

sudo chown $BOT_USER:$BOT_USER "$BOT_DIR/config_production.py"
sudo chmod 600 "$BOT_DIR/config_production.py"

print_success "Configuration template created"

# STEP 5: Create systemd service
print_header "STEP 5: SYSTEMD SERVICE SETUP"
print_status "Creating systemd service file..."

# Copy service file from repository or create new one
if [ -f "$BOT_DIR/gmail-bot.service" ]; then
    cp "$BOT_DIR/gmail-bot.service" "/etc/systemd/system/$SERVICE_NAME.service"
    print_success "Service file copied from repository"
else
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=Gmail Bot Telegram Service
After=network.target
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=$BOT_USER
Group=$BOT_USER
WorkingDirectory=$BOT_DIR
Environment=PATH=$BOT_DIR/venv/bin
ExecStart=$BOT_DIR/venv/bin/python $BOT_DIR/main.py
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
KillSignal=SIGINT
TimeoutStopSec=30

# Restart settings - auto restart on failure
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Resource limits
MemoryLimit=512M
CPUQuota=50%

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$BOT_DIR
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=gmail-bot

[Install]
WantedBy=multi-user.target
EOF
    print_success "Service file created"
fi

systemctl daemon-reload
systemctl enable $SERVICE_NAME

print_success "Service configured and enabled"

# STEP 6: Setup monitoring
print_header "STEP 6: MONITORING SETUP"
print_status "Setting up monitoring system..."

# Make monitoring scripts executable
chmod +x "$BOT_DIR/monitor.sh" 2>/dev/null || true
chmod +x "$BOT_DIR/backup.sh" 2>/dev/null || true
chmod +x "$BOT_DIR/bot_manager.sh" 2>/dev/null || true
chmod +x "$BOT_DIR/system_health_check.sh" 2>/dev/null || true

# Create symlink for easy management
ln -sf "$BOT_DIR/bot_manager.sh" /usr/local/bin/gmail-bot 2>/dev/null || true

# Setup cron jobs for automated monitoring and backup
print_status "Setting up cron jobs..."
sudo -u $BOT_USER bash -c "
# Create crontab for automated tasks
crontab -l 2>/dev/null | grep -v 'gmail-bot' > /tmp/crontab_new || true

# Add monitoring (every 5 minutes)
echo '*/5 * * * * $BOT_DIR/monitor.sh --quiet' >> /tmp/crontab_new

# Add backup (every 6 hours)
echo '0 */6 * * * $BOT_DIR/backup.sh --auto' >> /tmp/crontab_new

# Add health check (every hour)
echo '0 * * * * $BOT_DIR/system_health_check.sh --fix >/dev/null 2>&1' >> /tmp/crontab_new

# Add log cleanup (daily at 2 AM)
echo '0 2 * * * find $BOT_DIR/logs -name \"*.log.*\" -mtime +7 -delete' >> /tmp/crontab_new

# Install new crontab
crontab /tmp/crontab_new
rm /tmp/crontab_new
"

print_success "Automated monitoring and backup configured"

# STEP 7: Setup security
print_header "STEP 7: SECURITY CONFIGURATION"

# Configure UFW firewall
print_status "Configuring firewall..."
ufw --force reset >/dev/null 2>&1
ufw default deny incoming >/dev/null 2>&1
ufw default allow outgoing >/dev/null 2>&1

# Allow SSH
ufw allow ssh >/dev/null 2>&1

# Allow HTTP/HTTPS if webhook mode is used
if grep -q "WEBHOOK_MODE.*True" "$BOT_DIR/config_production.py" 2>/dev/null; then
    ufw allow 80 >/dev/null 2>&1
    ufw allow 443 >/dev/null 2>&1
    print_status "HTTP/HTTPS ports opened for webhook mode"
fi

ufw --force enable >/dev/null 2>&1
print_success "Firewall configured and enabled"

# Configure fail2ban
print_status "Configuring fail2ban..."
if [ ! -f "/etc/fail2ban/jail.local" ]; then
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s

[nginx-http-auth]
enabled = false

[nginx-noscript]
enabled = false

[nginx-badbots]
enabled = false

[nginx-noproxy]
enabled = false
EOF
fi

systemctl enable fail2ban >/dev/null 2>&1
systemctl restart fail2ban >/dev/null 2>&1
print_success "Fail2ban configured and started"

# Setup log rotation
print_status "Setting up log rotation..."
cat > /etc/logrotate.d/gmail-bot << EOF
$BOT_DIR/bot.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 $BOT_USER $BOT_USER
    postrotate
        systemctl reload $SERVICE_NAME > /dev/null 2>&1 || true
    endscript
}

$BOT_DIR/logs/*.log {
    weekly
    missingok
    rotate 4
    compress
    delaycompress
    notifempty
    create 644 $BOT_USER $BOT_USER
}
EOF

print_success "Log rotation configured"

# STEP 8: Final setup and verification
print_header "STEP 8: FINAL SETUP AND VERIFICATION"

# Set correct file permissions
print_status "Setting file permissions..."
chown -R $BOT_USER:$BOT_USER "$BOT_DIR"
chmod +x "$BOT_DIR"/*.sh 2>/dev/null || true

# Create empty log file
sudo -u $BOT_USER touch "$BOT_DIR/bot.log"

print_success "File permissions set correctly"

# Run initial health check
print_status "Running initial health check..."
if [ -f "$BOT_DIR/system_health_check.sh" ]; then
    sudo -u $BOT_USER "$BOT_DIR/system_health_check.sh" --fix || true
fi

print_success "Initial health check completed"

# STEP 9: Display completion message
print_header "DEPLOYMENT COMPLETED SUCCESSFULLY!"

echo -e "${GREEN}🎉 Gmail Bot deployment completed successfully!${NC}"
echo
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Edit configuration: nano $BOT_DIR/config_production.py"
echo "2. Upload Google credentials: nano $BOT_DIR/credentials.json"
echo "3. Start the bot: systemctl start $SERVICE_NAME"
echo "4. Check status: gmail-bot status"
echo "5. View logs: gmail-bot logs -f"
echo
echo -e "${YELLOW}📚 Management Commands:${NC}"
echo "• gmail-bot start      - Start bot"
echo "• gmail-bot stop       - Stop bot"
echo "• gmail-bot restart    - Restart bot"
echo "• gmail-bot status     - Show status"
echo "• gmail-bot logs       - View logs"
echo "• gmail-bot update     - Update from GitHub"
echo "• gmail-bot backup     - Create backup"
echo "• gmail-bot health     - Run health check"
echo
echo -e "${YELLOW}📁 Important Files:${NC}"
echo "• Config: $BOT_DIR/config_production.py"
echo "• Credentials: $BOT_DIR/credentials.json"
echo "• Logs: $BOT_DIR/logs/"
echo "• Backups: $BOT_DIR/backups/"
echo
echo -e "${YELLOW}🔒 Security Features Enabled:${NC}"
echo "• UFW Firewall ✅"
echo "• Fail2ban Protection ✅"
echo "• Auto Service Restart ✅"
echo "• Automated Monitoring ✅"
echo "• Automated Backups ✅"
echo "• Log Rotation ✅"
echo
echo -e "${CYAN}⚡ Ready for production! Configure your bot and start it.${NC}"
