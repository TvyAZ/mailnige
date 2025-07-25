# 🚀 **HƯỚNG DẪN DEPLOY HOÀN CHỈNH VPS UBUNTU - GMAIL BOT TELEGRAM**

## 📋 **MỤC LỤC**
1. [Chuẩn bị VPS và thông tin](#-chuẩn-bị-vps-và-thông-tin)
2. [Deploy tự động (Khuyến nghị)](#-deploy-tự-động-khuyến-nghị)
3. [Cấu hình Bot](#-cấu-hình-bot)
4. [Monitoring và Health Check](#-monitoring-và-health-check)
5. [Backup và Bảo mật](#-backup-và-bảo-mật)
6. [Quản lý Bot 24/7](#-quản-lý-bot-247)
7. [Troubleshooting](#-troubleshooting)

---

## 🎯 **CHUẨN BỊ VPS VÀ THÔNG TIN**

### **1. Yêu cầu VPS**
- **OS**: Ubuntu 20.04 LTS+ (khuyến nghị Ubuntu 22.04)
- **RAM**: Tối thiểu 512MB (khuyến nghị 1GB+)
- **Disk**: 5GB+ trống
- **CPU**: 1 core
- **Network**: Kết nối internet ổn định

### **2. Thông tin cần chuẩn bị**
- 🤖 **Bot Token** từ [@BotFather](https://t.me/BotFather)
- 👤 **Telegram Admin ID** (dùng [@userinfobot](https://t.me/userinfobot))
- 📊 **Google Sheets ID** (tạo Sheet mới trên Google Drive)
- 🔑 **Google Service Account JSON** (từ Google Cloud Console)
- 🏦 **Thông tin Bank** (STK, tên ngân hàng cho nạp tiền)

### **3. Tạo Google Service Account**
```bash
# 1. Vào Google Cloud Console: https://console.cloud.google.com/
# 2. Tạo project mới hoặc chọn project có sẵn
# 3. Enable Google Sheets API và Google Drive API
# 4. Tạo Service Account:
#    - IAM & Admin > Service Accounts > Create Service Account
#    - Tải file JSON credentials
# 5. Share Google Sheet với email service account (Editor access)
```

---

## ⚡ **DEPLOY TỰ ĐỘNG (KHUYẾN NGHỊ)**

### **Bước 1: Kết nối VPS**
```bash
# Kết nối SSH (thay your-vps-ip bằng IP thật của VPS)
ssh root@your-vps-ip

# Nếu dùng port SSH khác (ví dụ 2222)
ssh -p 2222 root@your-vps-ip
```

### **Bước 2: Deploy một lệnh duy nhất**
```bash
# ⚡ DEPLOY TỰ ĐỘNG HOÀN TOÀN (thay your-repo-url)
curl -sSL https://raw.githubusercontent.com/your-username/mailnige/main/production_deploy.sh | sudo bash -s -- https://github.com/your-username/mailnige.git
```

**📌 Lưu ý**: Thay `your-username/mailnige` bằng thông tin repository thật của bạn.

### **Bước 3: Kiểm tra deployment**
```bash
# Kiểm tra trạng thái deployment
sudo -u botuser bash -c "cd /home/botuser/gmail-bot && ./system_health_check.sh"
```

---

## 🔧 **CẤU HÌNH BOT**

### **1. Cấu hình chính**
```bash
# Chuyển sang user botuser
sudo -u botuser -i

# Di chuyển vào thư mục bot
cd /home/botuser/gmail-bot

# Cấu hình bot
nano config_production.py
```

**Nội dung file `config_production.py`:**
```python
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
```

### **2. Upload Google Credentials**
```bash
# Cách 1: Sử dụng nano để paste nội dung
nano credentials.json
# Paste nội dung file JSON từ Google Cloud Console

# Cách 2: Upload qua SCP (từ máy local)
# scp credentials.json root@your-vps-ip:/home/botuser/gmail-bot/

# Đảm bảo quyền file đúng
chown botuser:botuser credentials.json
chmod 600 credentials.json
```

### **3. Tạo Google Sheet**
```bash
# Chạy script tự động tạo Google Sheet structure
python3 -c "
import sys
sys.path.append('/home/botuser/gmail-bot')
from google_sheets import GoogleSheetsManager
gsm = GoogleSheetsManager()
gsm.setup_sheets()
print('✅ Google Sheets setup completed!')
"
```

---

## 📊 **MONITORING VÀ HEALTH CHECK**

### **1. Khởi động services**
```bash
# Khởi động bot service
systemctl start gmail-bot
systemctl enable gmail-bot

# Kiểm tra trạng thái
systemctl status gmail-bot

# Xem logs real-time
journalctl -u gmail-bot -f
```

### **2. Setup monitoring tự động**
```bash
# Cron job monitoring (đã được setup tự động)
crontab -l  # Xem các cron job đã được tạo

# Monitoring chạy mỗi 5 phút, tự động restart bot nếu cần
# Backup tự động mỗi 6 giờ
# Health check hệ thống mỗi giờ
```

### **3. Health check manual**
```bash
# Chạy health check toàn diện
sudo -u botuser /home/botuser/gmail-bot/system_health_check.sh

# Kiểm tra bot manager
gmail-bot health

# Xem logs chi tiết
gmail-bot logs --tail 100
```

---

## 🔒 **BACKUP VÀ BẢO MẬT**

### **1. Firewall setup (UFW)**
```bash
# Kiểm tra trạng thái firewall
ufw status

# Mở các port cần thiết
ufw allow ssh
ufw allow 80    # HTTP (nếu dùng webhook)
ufw allow 443   # HTTPS (nếu dùng webhook)

# Kích hoạt firewall
ufw --force enable
```

### **2. Fail2ban protection**
```bash
# Kiểm tra fail2ban
systemctl status fail2ban

# Xem các jail đang hoạt động
fail2ban-client status

# Xem IP bị ban
fail2ban-client status sshd
```

### **3. Backup system**
```bash
# Backup thủ công
gmail-bot backup

# Xem các backup có sẵn
ls -la /home/botuser/gmail-bot/backups/

# Restore từ backup
gmail-bot restore backup_20241201_120000.tar.gz
```

### **4. SSL/TLS (nếu dùng webhook)**
```bash
# Cài đặt Let's Encrypt cho domain
certbot --nginx -d yourdomain.com

# Auto-renewal certificate
systemctl enable certbot.timer
```

---

## 🎮 **QUẢN LÝ BOT 24/7**

### **1. Lệnh quản lý cơ bản**
```bash
gmail-bot start     # Khởi động bot
gmail-bot stop      # Dừng bot
gmail-bot restart   # Khởi động lại
gmail-bot status    # Trạng thái bot
gmail-bot logs      # Xem logs
gmail-bot logs -f   # Theo dõi logs real-time
```

### **2. Quản lý nâng cao**
```bash
gmail-bot update        # Cập nhật từ GitHub
gmail-bot backup        # Backup database
gmail-bot health        # Health check
gmail-bot cleanup       # Dọn dẹp logs cũ
gmail-bot config        # Xem cấu hình hiện tại
```

### **3. Xử lý sự cố**
```bash
# Bot không hoạt động
gmail-bot restart
gmail-bot health

# Bot bị crash liên tục
gmail-bot logs | grep -i error
systemctl status gmail-bot

# Database bị khóa
gmail-bot stop
sqlite3 /home/botuser/gmail-bot/gmail_bot.db ".timeout 30000"
gmail-bot start
```

### **4. Monitoring commands**
```bash
# CPU và Memory usage
htop

# Disk usage
df -h
du -sh /home/botuser/gmail-bot/

# Network connections
netstat -tlnp | grep python

# Process monitoring
ps aux | grep python
```

---

## 🆘 **TROUBLESHOOTING**

### **1. Bot không khởi động**
```bash
# Kiểm tra logs lỗi
journalctl -u gmail-bot --no-pager -l

# Kiểm tra config
python3 -c "import config_production; print('Config OK')"

# Kiểm tra dependencies
source venv/bin/activate
pip check

# Kiểm tra permissions
ls -la /home/botuser/gmail-bot/
```

### **2. Lỗi Google Sheets**
```bash
# Test Google Sheets connection
python3 -c "
from google_sheets import GoogleSheetsManager
gsm = GoogleSheetsManager()
print('Google Sheets connection:', gsm.test_connection())
"

# Kiểm tra credentials
ls -la credentials.json
python3 -c "import json; print(json.load(open('credentials.json'))['type'])"
```

### **3. Lỗi Database**
```bash
# Kiểm tra database
sqlite3 gmail_bot.db ".schema"
sqlite3 gmail_bot.db ".tables"

# Backup và tạo lại database
cp gmail_bot.db gmail_bot.db.backup
rm gmail_bot.db
python3 database.py  # Tạo lại database
```

### **4. Lỗi Memory**
```bash
# Kiểm tra memory usage
free -h
ps aux --sort=-%mem | head

# Restart bot để clear memory
gmail-bot restart

# Thêm swap nếu cần
fallocate -l 1G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 📞 **LIÊN HỆ HỖ TRỢ**

### **Log Files**
- Bot logs: `/home/botuser/gmail-bot/logs/`
- System logs: `journalctl -u gmail-bot`
- Error logs: `/var/log/syslog`

### **Cấu hình quan trọng**
- Config: `/home/botuser/gmail-bot/config_production.py`
- Service: `/etc/systemd/system/gmail-bot.service`
- Cron jobs: `crontab -u botuser -l`

### **Backup locations**
- Database backups: `/home/botuser/gmail-bot/backups/`
- System backups: `/opt/backups/gmail-bot/`

---

## ✅ **CHECKLIST HOÀN THÀNH**

- [ ] ✅ VPS đã được chuẩn bị
- [ ] ✅ Bot token đã được tạo  
- [ ] ✅ Google Service Account đã được setup
- [ ] ✅ Deploy script đã chạy thành công
- [ ] ✅ Config đã được cấu hình
- [ ] ✅ Google Sheets đã được setup
- [ ] ✅ Bot đã khởi động thành công
- [ ] ✅ Monitoring đã được kích hoạt
- [ ] ✅ Backup đã được setup
- [ ] ✅ Firewall đã được cấu hình
- [ ] ✅ Health check hoạt động tốt
- [ ] ✅ Bot đã test thành công

**🎉 Chúc mừng! Bot Gmail Telegram của bạn đã sẵn sàng hoạt động 24/7!**
