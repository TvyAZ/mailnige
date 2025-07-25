# 📖 Tổng quan dự án Gmail Bot

## 🎯 Mô tả dự án

**Gmail Bot** là một Telegram bot tự động bán tài khoản Gmail Nigeria với hệ thống quản lý hoàn chỉnh, được thiết kế để hoạt động trên VPS production một cách chuyên nghiệp.

## 🏗️ Kiến trúc hệ thống

```
Gmail Bot
├── 🤖 Bot Engine (main.py)
├── 👑 Admin Panel (admin_handlers.py)
├── 👤 User Interface (user_handlers.py)
├── ⌨️ Keyboard System (keyboards.py)
├── 🗄️ Database (database.py + SQLite)
├── 📊 Google Sheets (google_sheets.py)
├── ⚙️ Settings Manager (settings_manager.py)
├── 🚀 Deployment Scripts (*.sh)
└── 📚 Documentation (*.md)
```

## 🌟 Tính năng chính

### 👑 Admin Features
- **📊 Dashboard** - Thống kê tổng quan (users, revenue, deposits)
- **📧 Email Management** - Quản lý kho email, bulk import
- **👥 User Management** - Quản lý users, xem chi tiết user
- **💰 Financial Control** - Duyệt nạp tiền, xem lịch sử giao dịch
- **⚙️ Dynamic Settings** - Chỉnh sửa giá, chiết khấu, thông tin thanh toán
- **🔄 Batch Processing** - Xử lý hàng loạt với rate limiting

### 👤 User Features
- **💳 Deposit System** - Nạp tiền qua chuyển khoản
- **🛒 Purchase Gmail** - Mua email với giá động
- **📱 Account Management** - Xem số dư, lịch sử giao dịch
- **💬 Support** - Liên hệ admin trực tiếp
- **🎁 Discount System** - Hệ thống chiết khấu động

## 🔧 Technical Stack

### Backend
- **Python 3.9+** - Core language
- **python-telegram-bot** - Telegram API
- **SQLite** - Local database
- **Google Sheets API** - Cloud storage
- **asyncio** - Asynchronous processing

### Infrastructure
- **Ubuntu 20.04+** - Operating system
- **systemd** - Service management
- **nginx** - Reverse proxy (optional)
- **UFW** - Firewall
- **cron** - Scheduled tasks

### DevOps
- **Git** - Version control
- **GitHub Actions** - CI/CD
- **Shell Scripts** - Automation
- **Log rotation** - Log management
- **Backup automation** - Data protection

## 📁 Cấu trúc thư mục

```
/workspaces/mailnige/
├── 🐍 Python Files
│   ├── main.py              # Bot entry point
│   ├── admin_handlers.py    # Admin functionality
│   ├── user_handlers.py     # User functionality
│   ├── keyboards.py         # Keyboard layouts
│   ├── database.py          # Database operations
│   ├── google_sheets.py     # Google Sheets integration
│   ├── settings_manager.py  # Dynamic settings
│   └── config.py           # Configuration
│
├── 🚀 Deployment Scripts
│   ├── deploy.sh           # Main deployment
│   ├── github_deploy.sh    # GitHub deployment
│   ├── auto_update.sh      # Auto update
│   ├── quick_deploy.sh     # One-liner deploy
│   ├── bot_manager.sh      # Bot management
│   ├── monitor.sh          # System monitoring
│   └── setup_cron.sh       # Cron setup
│
├── 📚 Documentation
│   ├── README.md                   # Main documentation
│   ├── GITHUB_DEPLOY_GUIDE.md     # GitHub deployment
│   ├── VPS_DEPLOYMENT_GUIDE.md    # VPS deployment
│   ├── ADMIN_SETTINGS_GUIDE.md    # Admin settings
│   ├── VPS_README.md              # VPS management
│   ├── GITHUB_ACTIONS_GUIDE.md    # CI/CD setup
│   └── PROJECT_OVERVIEW.md        # This file
│
├── ⚙️ Configuration
│   ├── requirements.txt            # Python dependencies
│   ├── requirements_production.txt # Production dependencies
│   ├── .gitignore                 # Git ignore rules
│   └── config_production.py       # Production config
│
├── 🔄 CI/CD
│   └── .github/workflows/
│       └── deploy.yml             # GitHub Actions
│
└── 🗂️ Runtime (created during deployment)
    ├── logs/                      # Log files
    ├── backups/                   # Database backups
    ├── venv/                      # Virtual environment
    ├── gmail_bot.db              # SQLite database
    └── bot_settings.json         # Runtime settings
```

## 🚀 Deployment Options

### 1. 🔥 Quick Deploy (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/your-username/mailnige/main/quick_deploy.sh | sudo bash -s https://github.com/your-username/mailnige.git
```

### 2. 🎛️ GitHub Deploy
```bash
git clone https://github.com/your-username/mailnige.git
cd mailnige
sudo bash github_deploy.sh https://github.com/your-username/mailnige.git
```

### 3. 🔧 Manual Deploy
```bash
git clone https://github.com/your-username/mailnige.git
cd mailnige
sudo bash deploy.sh
sudo bash setup_bot.sh
```

## 🛠️ Management Commands

```bash
# Bot control
gmail-bot start     # Start bot
gmail-bot stop      # Stop bot
gmail-bot restart   # Restart bot
gmail-bot status    # Check status
gmail-bot logs      # View logs
gmail-bot update    # Update from GitHub
gmail-bot backup    # Backup database

# System monitoring
./monitor.sh        # Check system health
./bot_manager.sh    # Interactive management
```

## 🔐 Security Features

### 🛡️ Access Control
- **Admin-only functions** - Protected by user ID
- **Rate limiting** - Prevent API abuse
- **Input validation** - SQL injection prevention
- **Error handling** - Graceful error management

### 🔒 Data Protection
- **Database encryption** - SQLite with security
- **Credential isolation** - Separate config files
- **Log sanitization** - No sensitive data in logs
- **Backup encryption** - Secure backup storage

### 🚨 System Security
- **Firewall configuration** - UFW rules
- **SSH hardening** - Key-based authentication
- **Service isolation** - Non-root user
- **Auto-updates** - Security patches

## 📊 Monitoring & Analytics

### 📈 System Metrics
- **Service uptime** - systemd monitoring
- **Resource usage** - CPU, memory, disk
- **Database performance** - Query optimization
- **API rate limits** - Google Sheets monitoring

### 📋 Business Metrics
- **User growth** - Registration tracking
- **Revenue tracking** - Sales analytics
- **Conversion rates** - Purchase funnel
- **Support tickets** - User engagement

## 🔄 Maintenance

### 🔧 Regular Tasks
- **Database cleanup** - Old records removal
- **Log rotation** - Disk space management
- **Security updates** - System patches
- **Performance monitoring** - Resource optimization

### 📅 Scheduled Jobs
```bash
# Backup database (daily)
0 2 * * * /home/botuser/gmail-bot/backup.sh

# System health check (hourly)
0 * * * * /home/botuser/gmail-bot/monitor.sh

# Update bot (optional, weekly)
0 3 * * 0 /home/botuser/gmail-bot/auto_update.sh
```

## 🎯 Best Practices

### 🏆 Development
- **Code review** - All changes reviewed
- **Testing** - Unit and integration tests
- **Documentation** - Up-to-date docs
- **Version control** - Git workflow

### 🚀 Production
- **Zero downtime** - Rolling updates
- **Rollback ready** - Quick revert capability
- **Monitoring** - 24/7 health checks
- **Alerting** - Issue notifications

### 🔐 Security
- **Principle of least privilege** - Minimal permissions
- **Regular audits** - Security reviews
- **Incident response** - Emergency procedures
- **Compliance** - Legal requirements

## 📞 Support & Resources

### 📖 Documentation
- **User Guide** - End-user documentation
- **Admin Guide** - Administrator manual
- **API Reference** - Technical documentation
- **Troubleshooting** - Common issues

### 🆘 Support Channels
- **GitHub Issues** - Bug reports
- **Documentation** - Self-service help
- **Community** - User community
- **Direct Support** - Contact admin

## 🎉 Conclusion

Gmail Bot là một hệ thống hoàn chỉnh, được thiết kế để:

✅ **Scalable** - Có thể mở rộng dễ dàng
✅ **Maintainable** - Dễ bảo trì và cập nhật
✅ **Secure** - Bảo mật cao
✅ **Reliable** - Hoạt động ổn định 24/7
✅ **User-friendly** - Giao diện thân thiện
✅ **Production-ready** - Sẵn sàng commercial

Với hệ thống deployment tự động từ GitHub, monitoring toàn diện, và documentation chi tiết, dự án này có thể được deploy và vận hành chuyên nghiệp trên môi trường production.

---

**🚀 Ready to deploy?** 
Sử dụng quick deploy command và bắt đầu ngay:
```bash
curl -sSL https://raw.githubusercontent.com/your-username/mailnige/main/quick_deploy.sh | sudo bash -s https://github.com/your-username/mailnige.git
```
