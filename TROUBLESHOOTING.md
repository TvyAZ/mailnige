# 🔧 TROUBLESHOOTING GUIDE - Gmail Bot

## 🎯 Mục đích
Hướng dẫn chi tiết để chẩn đoán và khắc phục các vấn đề thường gặp khi deploy và vận hành Gmail Bot.

---

## 🚨 Các lỗi thường gặp

### ❌ 1. Bot không khởi động được

#### 🔍 Triệu chứng:
```bash
sudo systemctl status gmail-bot
# Output: failed (failed)
```

#### 🔧 Chẩn đoán:
```bash
# Kiểm tra logs chi tiết
sudo journalctl -u gmail-bot -n 50

# Kiểm tra config file
python3 -c "import config_production; print('Config OK')"

# Kiểm tra permissions
ls -la /home/botuser/gmail-bot/config_production.py
```

#### 💡 Giải pháp:
```bash
# Fix permissions
sudo chown -R botuser:botuser /home/botuser/gmail-bot/
chmod 600 /home/botuser/gmail-bot/config_production.py

# Recreate service
sudo systemctl daemon-reload
sudo systemctl restart gmail-bot
```

### ❌ 2. ModuleNotFoundError

#### 🔍 Triệu chứng:
```
ModuleNotFoundError: No module named 'telegram'
```

#### 🔧 Chẩn đoán:
```bash
# Kiểm tra virtual environment
ls -la /home/botuser/gmail-bot/venv/

# Kiểm tra installed packages
source /home/botuser/gmail-bot/venv/bin/activate
pip list | grep telegram
```

#### 💡 Giải pháp:
```bash
# Reinstall dependencies
cd /home/botuser/gmail-bot
source venv/bin/activate
pip install -r requirements.txt
# Hoặc
pip install -r requirements_production.txt
```

### ❌ 3. Google Sheets API Error

#### 🔍 Triệu chứng:
```
google.auth.exceptions.DefaultCredentialsError
```

#### 🔧 Chẩn đoán:
```bash
# Kiểm tra credentials file
ls -la /home/botuser/gmail-bot/credentials.json
cat /home/botuser/gmail-bot/credentials.json | head -5

# Test Google API
python3 -c "
from google_sheets import GoogleSheetsManager
from config_production import *
try:
    sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
    print('Google Sheets OK')
except Exception as e:
    print(f'Error: {e}')
"
```

#### 💡 Giải pháp:
```bash
# Fix credentials file
nano /home/botuser/gmail-bot/credentials.json
# Paste lại nội dung JSON từ Google Service Account

# Fix permissions
chmod 600 /home/botuser/gmail-bot/credentials.json

# Check Google Sheets sharing
# Đảm bảo đã share sheet với email service account
```

### ❌ 4. Database Lock Error

#### 🔍 Triệu chứng:
```
sqlite3.OperationalError: database is locked
```

#### 🔧 Chẩn đoán:
```bash
# Kiểm tra process sử dụng database
lsof /home/botuser/gmail-bot/gmail_bot.db

# Kiểm tra file lock
ls -la /home/botuser/gmail-bot/gmail_bot.db*
```

#### 💡 Giải pháp:
```bash
# Stop all processes
sudo systemctl stop gmail-bot
pkill -f "python.*main.py"

# Remove lock file
rm -f /home/botuser/gmail-bot/gmail_bot.db-wal
rm -f /home/botuser/gmail-bot/gmail_bot.db-shm

# Restart service
sudo systemctl start gmail-bot
```

### ❌ 5. Permission Denied

#### 🔍 Triệu chứng:
```
PermissionError: [Errno 13] Permission denied
```

#### 🔧 Chẩn đoán:
```bash
# Kiểm tra ownership
ls -la /home/botuser/gmail-bot/

# Kiểm tra permissions của các file quan trọng
ls -la /home/botuser/gmail-bot/config_production.py
ls -la /home/botuser/gmail-bot/credentials.json
ls -la /home/botuser/gmail-bot/gmail_bot.db
```

#### 💡 Giải pháp:
```bash
# Fix ownership
sudo chown -R botuser:botuser /home/botuser/gmail-bot/

# Fix permissions
chmod 755 /home/botuser/gmail-bot/
chmod 600 /home/botuser/gmail-bot/credentials.json
chmod 600 /home/botuser/gmail-bot/config_production.py
chmod 644 /home/botuser/gmail-bot/gmail_bot.db
```

### ❌ 6. Port Already in Use

#### 🔍 Triệu chứng:
```
OSError: [Errno 98] Address already in use
```

#### 🔧 Chẩn đoán:
```bash
# Kiểm tra processes đang chạy
ps aux | grep python
ps aux | grep main.py

# Kiểm tra ports
netstat -tlnp | grep python
```

#### 💡 Giải pháp:
```bash
# Kill duplicate processes
pkill -f "python.*main.py"

# Stop và start lại service
sudo systemctl stop gmail-bot
sleep 5
sudo systemctl start gmail-bot
```

### ❌ 7. Telegram API Error

#### 🔍 Triệu chứng:
```
telegram.error.Unauthorized: 401 Unauthorized
```

#### 🔧 Chẩn đoán:
```bash
# Kiểm tra Bot Token
grep BOT_TOKEN /home/botuser/gmail-bot/config_production.py

# Test token
curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
```

#### 💡 Giải pháp:
```bash
# Update Bot Token
nano /home/botuser/gmail-bot/config_production.py
# Paste token mới từ BotFather

# Restart bot
gmail-bot restart
```

### ❌ 8. Out of Memory

#### 🔍 Triệu chứng:
```
MemoryError: Unable to allocate memory
```

#### 🔧 Chẩn đoán:
```bash
# Kiểm tra memory usage
free -h
htop

# Kiểm tra swap
swapon --show
```

#### 💡 Giải pháp:
```bash
# Add swap file
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### ❌ 9. Disk Space Full

#### 🔍 Triệu chứng:
```
OSError: [Errno 28] No space left on device
```

#### 🔧 Chẩn đoán:
```bash
# Kiểm tra disk space
df -h

# Kiểm tra log files
du -sh /home/botuser/gmail-bot/logs/
du -sh /var/log/
```

#### 💡 Giải pháp:
```bash
# Clean logs
sudo journalctl --vacuum-time=7d
rm -f /home/botuser/gmail-bot/logs/*.log.1

# Setup log rotation
sudo nano /etc/logrotate.d/gmail-bot
```

### ❌ 10. Network Connection Error

#### 🔍 Triệu chứng:
```
requests.exceptions.ConnectionError
```

#### 🔧 Chẩn đoán:
```bash
# Test internet connection
ping -c 3 google.com
curl -I https://api.telegram.org

# Check firewall
sudo ufw status
```

#### 💡 Giải pháp:
```bash
# Allow outbound connections
sudo ufw allow out 443
sudo ufw allow out 80

# Restart networking
sudo systemctl restart networking
```

---

## 🔍 Diagnostic Commands

### 📊 System Health Check
```bash
#!/bin/bash
# comprehensive_check.sh

echo "=== SYSTEM HEALTH CHECK ==="
echo "Date: $(date)"
echo

echo "1. System Resources:"
echo "CPU Usage: $(top -bn1 | grep load | awk '{printf "%.2f%%", $(NF-2)*100}')"
echo "Memory: $(free -h | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')"
echo "Disk: $(df -h | awk '$NF=="/"{printf "%s", $5}')"
echo

echo "2. Service Status:"
systemctl is-active gmail-bot
systemctl is-enabled gmail-bot
echo

echo "3. Bot Process:"
ps aux | grep python | grep -v grep
echo

echo "4. Network:"
ping -c 1 google.com > /dev/null && echo "Internet: OK" || echo "Internet: FAILED"
curl -s https://api.telegram.org/bot$BOT_TOKEN/getMe > /dev/null && echo "Telegram API: OK" || echo "Telegram API: FAILED"
echo

echo "5. Files:"
ls -la /home/botuser/gmail-bot/config_production.py
ls -la /home/botuser/gmail-bot/credentials.json
ls -la /home/botuser/gmail-bot/gmail_bot.db
echo

echo "6. Logs (last 5 lines):"
tail -5 /home/botuser/gmail-bot/logs/bot.log
```

### 🔧 Bot Specific Check
```bash
#!/bin/bash
# bot_check.sh

echo "=== BOT SPECIFIC CHECK ==="
echo

echo "1. Config Test:"
cd /home/botuser/gmail-bot
source venv/bin/activate
python3 -c "
try:
    import config_production
    print('✅ Config loaded successfully')
    print(f'Bot Token: {config_production.BOT_TOKEN[:10]}...')
    print(f'Admin IDs: {config_production.ADMIN_IDS}')
except Exception as e:
    print(f'❌ Config error: {e}')
"

echo
echo "2. Dependencies Check:"
pip list | grep -E "(telegram|google|sqlite)"

echo
echo "3. Google Sheets Test:"
python3 -c "
try:
    from google_sheets import GoogleSheetsManager
    from config_production import *
    sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
    print('✅ Google Sheets connected')
except Exception as e:
    print(f'❌ Google Sheets error: {e}')
"

echo
echo "4. Database Test:"
python3 -c "
try:
    from database import Database
    from config_production import *
    db = Database(DATABASE_FILE)
    print('✅ Database connected')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

---

## 🚀 Recovery Procedures

### 🔄 Complete System Recovery
```bash
#!/bin/bash
# emergency_recovery.sh

echo "=== EMERGENCY RECOVERY ==="
echo "This will reset the bot to working state"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo "1. Stopping all processes..."
sudo systemctl stop gmail-bot
pkill -f "python.*main.py"

echo "2. Backing up current state..."
cd /home/botuser/gmail-bot
cp gmail_bot.db backups/emergency_backup_$(date +%Y%m%d_%H%M%S).db
cp bot_settings.json backups/settings_backup_$(date +%Y%m%d_%H%M%S).json

echo "3. Cleaning temporary files..."
rm -f gmail_bot.db-wal gmail_bot.db-shm
rm -f logs/*.log.1

echo "4. Fixing permissions..."
sudo chown -R botuser:botuser /home/botuser/gmail-bot/
chmod 600 credentials.json config_production.py
chmod 755 *.sh

echo "5. Reinstalling dependencies..."
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

echo "6. Restarting service..."
sudo systemctl daemon-reload
sudo systemctl start gmail-bot
sudo systemctl enable gmail-bot

echo "7. Checking status..."
sleep 5
sudo systemctl status gmail-bot
```

### 🔧 Quick Fix Script
```bash
#!/bin/bash
# quick_fix.sh

echo "=== QUICK FIX ==="

# Fix permissions
sudo chown -R botuser:botuser /home/botuser/gmail-bot/

# Restart service
sudo systemctl restart gmail-bot

# Check status
sleep 3
if systemctl is-active --quiet gmail-bot; then
    echo "✅ Bot is running"
else
    echo "❌ Bot failed to start"
    echo "Recent logs:"
    sudo journalctl -u gmail-bot -n 10
fi
```

---

## 📞 Support Escalation

### 🎯 Level 1: Self-Service
1. Check this troubleshooting guide
2. Run diagnostic scripts
3. Check logs
4. Try quick fixes

### 🎯 Level 2: Community Support
1. Search GitHub Issues
2. Check documentation
3. Ask in community forums
4. Post detailed error logs

### 🎯 Level 3: Advanced Support
1. Collect system information
2. Generate diagnostic report
3. Contact technical support
4. Provide access for debugging

### 📋 Information to collect:
```bash
# System info
uname -a
cat /etc/os-release
free -h
df -h

# Bot info
sudo systemctl status gmail-bot
sudo journalctl -u gmail-bot -n 100
python3 --version
pip list

# Configuration (remove sensitive data)
cat config_production.py | grep -v TOKEN | grep -v ADMIN_IDS
```

---

## 🔄 Preventive Measures

### 📊 Monitoring Setup
```bash
# Add to crontab
0 */6 * * * /home/botuser/gmail-bot/monitor.sh
0 2 * * * /home/botuser/gmail-bot/backup.sh
```

### 🛡️ Health Checks
```bash
# Create health check endpoint
curl -f http://localhost:8080/health || gmail-bot restart
```

### 📱 Alerting
```bash
# Send alert when bot fails
systemctl status gmail-bot | grep -q "failed" && echo "Bot failed" | mail -s "Alert" admin@example.com
```

---

## 🎓 Best Practices

### ✅ DO:
- Always backup before making changes
- Test changes in development first
- Monitor logs regularly
- Keep dependencies updated
- Use proper permissions
- Document changes

### ❌ DON'T:
- Run bot as root
- Ignore permission errors
- Skip backups
- Hardcode sensitive data
- Ignore logs
- Make changes without testing

---

**🚀 Remember: Most issues can be resolved with proper diagnosis and systematic troubleshooting!**

*Keep this guide handy for quick problem resolution.*
