# 🚀 QUICK REFERENCE: Gmail Bot Deployment

## ⚡ TL;DR - Deploy trong 5 phút

```bash
# 1. Chuẩn bị VPS
ssh root@your-vps-ip
apt update && apt upgrade -y
apt install -y git python3 python3-pip python3-venv curl

# 2. One-liner deploy
curl -sSL https://raw.githubusercontent.com/your-username/your-repo/main/quick_deploy.sh | sudo bash -s https://github.com/your-username/your-repo.git

# 3. Cấu hình
nano /home/botuser/gmail-bot/config_production.py
nano /home/botuser/gmail-bot/credentials.json

# 4. Khởi động
gmail-bot start
```

---

## 📋 Checklist Deploy

### ✅ Pre-deployment
- [ ] VPS Ubuntu 20.04+ (512MB RAM, 2GB disk)
- [ ] Bot Token từ @BotFather
- [ ] Admin Telegram ID
- [ ] Google Service Account JSON
- [ ] Google Sheets ID
- [ ] GitHub repository đã có code

### ✅ Deployment
- [ ] SSH kết nối VPS thành công
- [ ] System updated và dependencies installed
- [ ] User botuser đã tạo
- [ ] Repository cloned và scripts executable
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] systemd service created

### ✅ Configuration
- [ ] config_production.py đã điền đầy đủ thông tin
- [ ] credentials.json uploaded
- [ ] File permissions đã set đúng
- [ ] Bot test thành công
- [ ] Service khởi động được

### ✅ Post-deployment
- [ ] Bot hoạt động trên Telegram
- [ ] Admin panel accessible
- [ ] Google Sheets connected
- [ ] Monitoring setup
- [ ] Backup scheduled
- [ ] Firewall configured

---

## 🔧 Essential Commands

### 🤖 Bot Management
```bash
gmail-bot start         # Khởi động bot
gmail-bot stop          # Dừng bot
gmail-bot restart       # Restart bot
gmail-bot status        # Xem trạng thái
gmail-bot logs          # Xem logs
gmail-bot update        # Update từ GitHub
gmail-bot backup        # Backup database
```

### 📊 System Commands
```bash
# Service management
sudo systemctl start gmail-bot
sudo systemctl stop gmail-bot
sudo systemctl restart gmail-bot
sudo systemctl status gmail-bot

# Logs
sudo journalctl -u gmail-bot -f
tail -f /home/botuser/gmail-bot/logs/bot.log

# Monitoring
htop
df -h
free -h
```

### 🔍 Troubleshooting
```bash
# Check processes
ps aux | grep python

# Check files
ls -la /home/botuser/gmail-bot/
ls -la /home/botuser/gmail-bot/venv/

# Test bot
cd /home/botuser/gmail-bot
source venv/bin/activate
python main.py

# Fix permissions
sudo chown -R botuser:botuser /home/botuser/gmail-bot/
```

---

## 📝 Configuration Templates

### 🔑 config_production.py
```python
BOT_TOKEN = "1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
ADMIN_IDS = [123456789]
GOOGLE_SHEETS_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
GOOGLE_CREDENTIALS_FILE = "/home/botuser/gmail-bot/credentials.json"
DATABASE_FILE = "/home/botuser/gmail-bot/gmail_bot.db"
LOG_FILE = "/home/botuser/gmail-bot/logs/bot.log"
```

### 🔐 credentials.json
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@your-project.iam.gserviceaccount.com"
}
```

---

## 🆘 Common Issues & Solutions

### ❌ Bot không start
```bash
# Check logs
sudo journalctl -u gmail-bot -n 20

# Check config
python3 -c "import config_production; print('OK')"

# Check permissions
ls -la /home/botuser/gmail-bot/config_production.py
```

### ❌ Google Sheets error
```bash
# Check credentials
ls -la /home/botuser/gmail-bot/credentials.json

# Test connection
python3 -c "from google_sheets import GoogleSheetsManager; print('OK')"
```

### ❌ Database error
```bash
# Check database
ls -la /home/botuser/gmail-bot/gmail_bot.db

# Recreate database
rm gmail_bot.db
gmail-bot restart
```

### ❌ Permission denied
```bash
# Fix all permissions
sudo chown -R botuser:botuser /home/botuser/gmail-bot/
chmod 600 /home/botuser/gmail-bot/credentials.json
chmod 600 /home/botuser/gmail-bot/config_production.py
```

---

## 🔄 Update & Maintenance

### 📦 Update bot
```bash
# Manual update
cd /home/botuser/gmail-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
gmail-bot restart

# Auto update
bash auto_update.sh
```

### 🗂️ Backup
```bash
# Manual backup
cp gmail_bot.db backups/backup_$(date +%Y%m%d).db
cp bot_settings.json backups/settings_$(date +%Y%m%d).json

# Check auto backup
crontab -l
ls -la backups/
```

### 📊 Monitoring
```bash
# System health
./monitor.sh

# Service health
sudo systemctl is-active gmail-bot
sudo systemctl is-enabled gmail-bot

# Resource usage
htop
df -h
```

---

## 🔐 Security Checklist

### 🛡️ VPS Security
- [ ] UFW firewall enabled
- [ ] SSH port changed (optional)
- [ ] Root login disabled
- [ ] Key-based authentication
- [ ] Fail2ban installed (optional)
- [ ] Regular updates scheduled

### 🔒 Bot Security
- [ ] Credentials files secured (600 permissions)
- [ ] Admin IDs correctly configured
- [ ] Input validation enabled
- [ ] Rate limiting active
- [ ] Logs don't contain sensitive data

---

## 📞 Support Resources

### 📖 Documentation
- **[DETAILED_DEPLOYMENT_GUIDE.md](DETAILED_DEPLOYMENT_GUIDE.md)** - Chi tiết từng bước
- **[ADMIN_SETTINGS_GUIDE.md](ADMIN_SETTINGS_GUIDE.md)** - Cấu hình admin
- **[VPS_README.md](VPS_README.md)** - Quản lý VPS
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Sửa lỗi

### 🛠️ Tools
- **bot_manager.sh** - Interactive management
- **monitor.sh** - System monitoring
- **auto_update.sh** - Automatic updates
- **backup.sh** - Database backup

### 🔍 Debug Commands
```bash
# Full system check
./monitor.sh
gmail-bot status
sudo journalctl -u gmail-bot --since "1 hour ago"
python3 -c "import config_production; print('Config loaded')"
```

---

## 🎯 Production Optimization

### ⚡ Performance
```bash
# Optimize Python
export PYTHONOPTIMIZE=1

# Log rotation
sudo nano /etc/logrotate.d/gmail-bot

# Memory limits
sudo systemctl edit gmail-bot
```

### 📊 Monitoring
```bash
# Setup monitoring
./setup_cron.sh

# Custom monitoring
watch -n 5 'gmail-bot status'
```

### 🔄 High Availability
```bash
# Auto-restart on failure
sudo systemctl enable gmail-bot

# Health check endpoint
curl -f http://localhost:8080/health || gmail-bot restart
```

---

## 🎉 Success Indicators

### ✅ Deployment Success
- Service status: `active (running)`
- Logs show: `Bot đang khởi động...`
- Telegram bot responds to `/start`
- Admin panel accessible
- Google Sheets connected

### 📊 Health Metrics
- CPU usage: < 20%
- Memory usage: < 200MB
- Disk usage: < 80%
- Response time: < 2 seconds
- Uptime: > 99%

---

**🚀 Ready to deploy? Follow this guide and your bot will be live in minutes!**

*Keep this reference handy for quick troubleshooting and maintenance.*
