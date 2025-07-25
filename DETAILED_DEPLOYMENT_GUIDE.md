# 🚀 HƯỚNG DẪN DEPLOY CHI TIẾT - GMAIL BOT

## 📋 Mục lục
1. [Chuẩn bị trước khi deploy](#-chuẩn-bị-trước-khi-deploy)
2. [Bước 1: Chuẩn bị VPS Ubuntu](#-bước-1-chuẩn-bị-vps-ubuntu)
3. [Bước 2: Chuẩn bị repository GitHub](#-bước-2-chuẩn-bị-repository-github)
4. [Bước 3: Deploy bot lên VPS](#-bước-3-deploy-bot-lên-vps)
5. [Bước 4: Cấu hình bot](#-bước-4-cấu-hình-bot)
6. [Bước 5: Khởi động và kiểm tra](#-bước-5-khởi-động-và-kiểm-tra)
7. [Bước 6: Setup monitoring và backup](#-bước-6-setup-monitoring-và-backup)
8. [Bước 7: Bảo mật VPS](#-bước-7-bảo-mật-vps)
9. [Troubleshooting](#-troubleshooting)

---

## 📝 Chuẩn bị trước khi deploy

### 🎯 Những gì bạn cần có:
- **VPS Ubuntu 20.04+** (512MB RAM, 2GB disk)
- **Bot Token** từ @BotFather
- **Admin Telegram ID** của bạn
- **Google Service Account** với Sheets API
- **Google Sheets** đã tạo sẵn
- **Repository GitHub** (public hoặc private)

### 🔧 Tools cần thiết:
- SSH client (Terminal, PuTTY)
- Text editor (nano, vim)
- Git (để clone repository)

---

## 🖥️ Bước 1: Chuẩn bị VPS Ubuntu

### 1.1. Kết nối SSH vào VPS
```bash
# Kết nối SSH (thay IP và user thực tế)
ssh root@your-vps-ip

# Hoặc nếu dùng port khác
ssh -p 2222 root@your-vps-ip
```

### 1.2. Cập nhật hệ thống
```bash
# Cập nhật package list
apt update

# Upgrade hệ thống
apt upgrade -y

# Cài đặt các gói cần thiết
apt install -y git python3 python3-pip python3-venv curl wget nano ufw htop
```

### 1.3. Tạo user để chạy bot (không dùng root)
```bash
# Tạo user mới
adduser botuser

# Thêm user vào sudo group
usermod -aG sudo botuser

# Chuyển sang user botuser
su - botuser
```

### 1.4. Kiểm tra Python version
```bash
python3 --version
# Phải có Python 3.9+
```

---

## 📦 Bước 2: Chuẩn bị repository GitHub

### 2.1. Fork hoặc clone repository
```bash
# Nếu bạn fork repository, thay your-username và your-repo-name
git clone https://github.com/your-username/your-repo-name.git

# Hoặc clone repository gốc
git clone https://github.com/original-owner/mailnige.git
```

### 2.2. Cập nhật thông tin repository (nếu cần)
```bash
cd your-repo-name

# Chạy script để cập nhật thông tin repository
bash update_repo_info.sh your-username/your-repo-name

# Ví dụ:
bash update_repo_info.sh johndoe/gmail-bot-vietnam
```

### 2.3. Push lên GitHub (nếu có thay đổi)
```bash
git add .
git commit -m "Update repository info"
git push origin main
```

---

## 🚀 Bước 3: Deploy bot lên VPS

### 3.1. Cách 1: Quick Deploy (Khuyến nghị)
```bash
# One-liner deploy (thay URL repository thực tế)
curl -sSL https://raw.githubusercontent.com/your-username/your-repo/main/quick_deploy.sh | sudo bash -s https://github.com/your-username/your-repo.git
```

### 3.2. Cách 2: Manual deploy
```bash
# Clone repository trên VPS
cd /home/botuser
git clone https://github.com/your-username/your-repo.git gmail-bot
cd gmail-bot

# Cấp quyền execute cho scripts
chmod +x *.sh

# Chạy script deploy
sudo bash deploy.sh

# Chạy script setup bot
sudo bash setup_bot.sh
```

### 3.3. Kiểm tra deploy thành công
```bash
# Kiểm tra thư mục bot
ls -la /home/botuser/gmail-bot/

# Kiểm tra virtual environment
ls -la /home/botuser/gmail-bot/venv/

# Kiểm tra service
sudo systemctl status gmail-bot
```

---

## ⚙️ Bước 4: Cấu hình bot

### 4.1. Tạo Bot Token từ BotFather
```
1. Mở Telegram, tìm @BotFather
2. Gửi /newbot
3. Nhập tên bot: Gmail Bot Vietnam
4. Nhập username: gmail_bot_vietnam_bot
5. Lưu Bot Token: 1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

### 4.2. Lấy Admin Telegram ID
```
1. Mở Telegram, tìm @userinfobot
2. Gửi /start
3. Lưu User ID: 123456789
```

### 4.3. Cấu hình Google Sheets API

#### Bước 4.3.1: Tạo Google Service Account
```
1. Vào Google Cloud Console: https://console.cloud.google.com/
2. Tạo project mới hoặc chọn project có sẵn
3. Enable Google Sheets API
4. Tạo Service Account:
   - IAM & Admin > Service Accounts
   - Create Service Account
   - Tên: gmail-bot-service
   - Role: Editor
5. Tạo key JSON và download
```

#### Bước 4.3.2: Tạo Google Sheets
```
1. Vào Google Sheets: https://sheets.google.com/
2. Tạo sheet mới
3. Đặt tên: Gmail Bot Database
4. Share sheet với email service account
5. Lưu Sheet ID từ URL:
   https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
   Sheet ID: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

### 4.4. Cấu hình file config
```bash
# Chỉnh sửa config production
nano /home/botuser/gmail-bot/config_production.py
```

**Nội dung cấu hình:**
```python
# Production Configuration for Gmail Bot
# =======================================

# Bot Configuration
BOT_TOKEN = "1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"  # Bot token từ BotFather
ADMIN_IDS = [123456789]  # Telegram ID của bạn

# Google Sheets Configuration
GOOGLE_SHEETS_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"  # Sheet ID
GOOGLE_CREDENTIALS_FILE = "/home/botuser/gmail-bot/credentials.json"

# Database Configuration
DATABASE_FILE = "/home/botuser/gmail-bot/gmail_bot.db"
SETTINGS_FILE = "/home/botuser/gmail-bot/bot_settings.json"

# Logging Configuration
LOG_FILE = "/home/botuser/gmail-bot/logs/bot.log"
LOG_LEVEL = "INFO"

# Rate Limiting
SHEETS_RATE_LIMIT = 2
MAX_RETRIES = 3
RETRY_DELAY = 5

# Bot Settings
DEFAULT_GMAIL_PRICE = 5000  # 5,000 VND
DEFAULT_DISCOUNT_PERCENT = 0
MIN_DEPOSIT = 10000  # 10,000 VND

# Bank Info
BANK_INFO = {
    "bank": "Vietcombank",
    "account": "1234567890",
    "name": "NGUYEN VAN A"
}

# Contact
CONTACT_INFO = "@admin_username"

# Security
DEBUG = False
```

### 4.5. Upload Google Credentials
```bash
# Tạo file credentials.json
nano /home/botuser/gmail-bot/credentials.json
```

**Paste nội dung JSON từ Google Service Account:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "gmail-bot-service@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs/gmail-bot-service%40your-project.iam.gserviceaccount.com"
}
```

### 4.6. Thiết lập permissions
```bash
# Đảm bảo ownership đúng
sudo chown -R botuser:botuser /home/botuser/gmail-bot/

# Bảo mật file credentials
chmod 600 /home/botuser/gmail-bot/credentials.json
chmod 600 /home/botuser/gmail-bot/config_production.py
```

---

## 🎯 Bước 5: Khởi động và kiểm tra

### 5.1. Test bot trước khi khởi động service
```bash
# Chuyển vào thư mục bot
cd /home/botuser/gmail-bot

# Activate virtual environment
source venv/bin/activate

# Test bot
python main.py
```

**Nếu thấy thông báo này là thành công:**
```
INFO - 🤖 Bot đang khởi động...
INFO - 📊 Admin IDs: [123456789]
INFO - Đã kết nối Google Sheets thành công
INFO - Application started
```

**Nhấn Ctrl+C để dừng test**

### 5.2. Khởi động bot bằng systemd service
```bash
# Khởi động service
sudo systemctl start gmail-bot

# Kiểm tra trạng thái
sudo systemctl status gmail-bot

# Kích hoạt auto-start khi reboot
sudo systemctl enable gmail-bot
```

### 5.3. Kiểm tra logs
```bash
# Xem logs realtime
sudo journalctl -u gmail-bot -f

# Xem logs gần đây
sudo journalctl -u gmail-bot --since "10 minutes ago"

# Xem log file
tail -f /home/botuser/gmail-bot/logs/bot.log
```

### 5.4. Test bot trên Telegram
```
1. Mở Telegram
2. Tìm bot của bạn: @your_bot_username
3. Gửi /start
4. Kiểm tra các chức năng:
   - Admin panel (nếu bạn là admin)
   - User functions
   - Keyboard buttons
   - Google Sheets integration
```

---

## 📊 Bước 6: Setup monitoring và backup

### 6.1. Chạy script setup monitoring
```bash
cd /home/botuser/gmail-bot

# Setup cron jobs cho monitoring và backup
sudo bash setup_cron.sh

# Kiểm tra cron jobs đã được tạo
crontab -l
```

### 6.2. Kiểm tra monitoring hoạt động
```bash
# Chạy monitoring thủ công
./monitor.sh

# Kiểm tra backup
ls -la backups/
```

### 6.3. Setup log rotation
```bash
# Tạo logrotate config
sudo nano /etc/logrotate.d/gmail-bot
```

**Nội dung:**
```
/home/botuser/gmail-bot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    missingok
    copytruncate
    su botuser botuser
}
```

---

## 🔒 Bước 7: Bảo mật VPS

### 7.1. Cấu hình UFW Firewall
```bash
# Kích hoạt UFW
sudo ufw enable

# Cho phép SSH
sudo ufw allow ssh
sudo ufw allow 22

# Nếu dùng port SSH khác
sudo ufw allow 2222

# Kiểm tra status
sudo ufw status
```

### 7.2. Bảo mật SSH
```bash
# Backup SSH config
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Chỉnh sửa SSH config
sudo nano /etc/ssh/sshd_config
```

**Cấu hình khuyến nghị:**
```
# Đổi port SSH (tùy chọn)
Port 2222

# Không cho phép root login
PermitRootLogin no

# Chỉ cho phép user cụ thể
AllowUsers botuser

# Tăng cường bảo mật
Protocol 2
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

```bash
# Restart SSH service
sudo systemctl restart ssh
```

### 7.3. Setup fail2ban (tùy chọn)
```bash
# Cài đặt fail2ban
sudo apt install fail2ban

# Cấu hình fail2ban
sudo nano /etc/fail2ban/jail.local
```

**Nội dung:**
```
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
```

```bash
# Khởi động fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 🔧 Quản lý bot sau khi deploy

### 📋 Lệnh quản lý cơ bản
```bash
# Khởi động bot
gmail-bot start

# Dừng bot
gmail-bot stop

# Khởi động lại bot
gmail-bot restart

# Xem trạng thái bot
gmail-bot status

# Xem logs
gmail-bot logs

# Cập nhật bot từ GitHub
gmail-bot update

# Backup database
gmail-bot backup
```

### 🔄 Cập nhật bot
```bash
# Cập nhật tự động từ GitHub
cd /home/botuser/gmail-bot
bash auto_update.sh

# Hoặc sử dụng lệnh quản lý
gmail-bot update
```

### 📊 Monitoring
```bash
# Xem resource usage
htop

# Xem disk usage
df -h

# Xem memory usage
free -h

# Xem service status
sudo systemctl status gmail-bot
```

---

## 🆘 Troubleshooting

### ❌ Lỗi thường gặp và cách khắc phục

#### 1. Bot không khởi động được
```bash
# Kiểm tra logs
sudo journalctl -u gmail-bot -n 50

# Kiểm tra config
python3 -c "import config_production; print('Config OK')"

# Kiểm tra dependencies
source venv/bin/activate
pip list | grep telegram
```

#### 2. Google Sheets không kết nối được
```bash
# Kiểm tra credentials file
ls -la credentials.json
cat credentials.json | head -5

# Test Google Sheets connection
python3 -c "
from google_sheets import GoogleSheetsManager
from config_production import *
sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
print('Google Sheets OK')
"
```

#### 3. Database lỗi
```bash
# Kiểm tra database file
ls -la gmail_bot.db

# Backup và recreate database
cp gmail_bot.db gmail_bot.db.backup
rm gmail_bot.db

# Restart bot để tạo database mới
gmail-bot restart
```

#### 4. Permission denied
```bash
# Fix permissions
sudo chown -R botuser:botuser /home/botuser/gmail-bot/
chmod +x /home/botuser/gmail-bot/*.sh
```

#### 5. Service không start
```bash
# Kiểm tra service file
sudo systemctl cat gmail-bot

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl restart gmail-bot
```

### 🔍 Debug commands hữu ích
```bash
# Kiểm tra process
ps aux | grep python

# Kiểm tra ports
netstat -tlnp | grep python

# Kiểm tra system resources
top -u botuser

# Kiểm tra disk space
du -sh /home/botuser/gmail-bot/

# Kiểm tra logs size
du -sh /home/botuser/gmail-bot/logs/
```

---

## 📞 Hỗ trợ

### 📖 Tài liệu tham khảo
- **README.md** - Hướng dẫn tổng quan
- **ADMIN_SETTINGS_GUIDE.md** - Cấu hình admin
- **VPS_README.md** - Quản lý VPS
- **GITHUB_ACTIONS_GUIDE.md** - Setup CI/CD

### 🔧 Tools hỗ trợ
- **bot_manager.sh** - Quản lý bot interactive
- **monitor.sh** - Monitoring hệ thống
- **auto_update.sh** - Cập nhật tự động

### 📊 Monitoring dashboard
```bash
# Chạy monitoring interactive
./bot_manager.sh

# Xem system stats
./monitor.sh
```

---

## 🎉 Kết luận

**Chúc mừng!** Bạn đã deploy thành công Gmail Bot lên VPS Ubuntu!

### ✅ Những gì đã hoàn thành:
- ✅ VPS Ubuntu đã được cấu hình và bảo mật
- ✅ Bot Telegram đã được deploy và chạy ổn định
- ✅ Google Sheets đã được kết nối
- ✅ Monitoring và backup đã được setup
- ✅ Systemd service đã được cấu hình

### 🎯 Bước tiếp theo:
1. **Test đầy đủ các chức năng** trên Telegram
2. **Thêm email vào kho** qua admin panel
3. **Cấu hình thông tin thanh toán** và liên hệ
4. **Monitor bot** trong vài ngày đầu
5. **Setup backup định kỳ** cho database

### 📞 Liên hệ hỗ trợ:
- **GitHub Issues** - Báo cáo lỗi
- **Documentation** - Đọc tài liệu
- **Community** - Cộng đồng người dùng

---

**🚀 Bot của bạn đã sẵn sàng phục vụ khách hàng!**

*Happy deploying! 🎊*
