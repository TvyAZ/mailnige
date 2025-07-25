# 🤖 Gmail Bot - Telegram Bot bán Gmail Nigeria

![Deploy Status](https://img.shields.io/badge/deploy-ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Production](https://img.shields.io/badge/production-ready-success)

Bot Telegram tự động bán tài khoản Gmail Nigeria với hệ thống quản lý hoàn chỉnh, được thiết kế cho production VPS với **monitoring 24/7**, **auto-restart**, **backup tự động**, và **bảo mật cao**.

## ✨ Tính năng chính

### 👑 Admin Features
- **📊 Dashboard** - Thống kê tổng quan (users, revenue, deposits)
- **📧 Email Management** - Quản lý kho email, bulk import (100 email/lần)
- **👥 User Management** - Quản lý users, xem chi tiết
- **💰 Financial Control** - Duyệt nạp tiền, lịch sử giao dịch
- **⚙️ Dynamic Settings** - Chỉnh sửa giá, chiết khấu, thông tin thanh toán
- **🔄 Batch Processing** - Xử lý hàng loạt với rate limiting

### 👤 User Features
- **💳 Deposit System** - Nạp tiền qua chuyển khoản
- **🛒 Purchase Gmail** - Mua email với giá động
- **📱 Account Management** - Xem số dư, lịch sử giao dịch
- **💬 Support** - Liên hệ admin trực tiếp
- **🎁 Discount System** - Hệ thống chiết khấu động

### 🏭 Production Features
- **🔄 Auto-restart** - Tự động khởi động lại khi crash
- **📊 24/7 Monitoring** - Giám sát liên tục, cảnh báo sớm
- **💾 Auto Backup** - Backup tự động mỗi 6 giờ
- **🔒 Security** - Firewall, Fail2ban, log rotation
- **📈 Health Check** - Kiểm tra sức khỏe hệ thống
- **🎛️ Easy Management** - Quản lý dễ dàng qua CLI

## 🚀 Deploy VPS Ubuntu - Production Ready

### ⚡ Cách 1: Deploy Tự Động (Khuyến nghị)
```bash
# 🔥 DEPLOY HOÀN TOÀN TỰ ĐỘNG - Chỉ 1 lệnh!
curl -sSL https://raw.githubusercontent.com/your-username/mailnige/main/production_deploy.sh | sudo bash -s -- https://github.com/your-username/mailnige.git

# Sau đó cấu hình:
nano /home/botuser/gmail-bot/config_production.py
nano /home/botuser/gmail-bot/credentials.json

# Khởi động bot:
gmail-bot start
```

### 🎛️ Cách 2: Clone và Deploy
```bash
# Clone repository
git clone https://github.com/your-username/mailnige.git
cd mailnige

# Deploy production
sudo bash production_deploy.sh https://github.com/your-username/mailnige.git

# Cấu hình và khởi động
gmail-bot config
gmail-bot start
```

### 🔧 Cách 3: Manual Setup
```bash
# Xem hướng dẫn chi tiết
cat COMPLETE_VPS_DEPLOYMENT.md
```

## ⚠️ Bước đầu tiên: Cập nhật thông tin repository

**QUAN TRỌNG**: Trước khi deploy, phải thay đổi thông tin repository:

```bash
# Thay your-username/mailnige bằng thông tin repo thật
# Cập nhật trong các file:
# - production_deploy.sh
# - README.md  
# - COMPLETE_VPS_DEPLOYMENT.md
```

## 🎮 Quản lý Bot Production

### **Lệnh cơ bản**
```bash
gmail-bot start     # 🚀 Khởi động bot
gmail-bot stop      # ⏹️ Dừng bot
gmail-bot restart   # 🔄 Khởi động lại bot
gmail-bot status    # 📊 Xem trạng thái chi tiết
gmail-bot logs      # 📝 Xem logs
gmail-bot logs -f   # 👀 Theo dõi logs realtime
```

### **Lệnh nâng cao**
```bash
gmail-bot update    # 🔄 Cập nhật từ GitHub
gmail-bot backup    # 💾 Backup database & config
gmail-bot health    # 🏥 Kiểm tra sức khỏe toàn diện
gmail-bot cleanup   # 🧹 Dọn dẹp files cũ
gmail-bot config    # ⚙️ Xem cấu hình hiện tại
```

## 📊 Monitoring & Health Check

### **Automated Monitoring**
- ✅ **Health check** mỗi 5 phút
- ✅ **Auto-restart** khi phát hiện lỗi
- ✅ **Memory/CPU monitoring**
- ✅ **Disk space monitoring**
- ✅ **API connectivity check**

### **Manual Health Check**
```bash
# Kiểm tra toàn diện
gmail-bot health

# Kiểm tra với fix tự động
sudo -u botuser /home/botuser/gmail-bot/system_health_check_production.sh --fix

# Xem trạng thái chi tiết
gmail-bot status
```

## 💾 Backup & Restore

### **Automated Backup**
- ✅ **Backup tự động** mỗi 6 giờ
- ✅ **Database + Config backup**
- ✅ **Keep 10 local, 30 remote backups**
- ✅ **Automatic cleanup old backups**

### **Manual Backup**
```bash
# Tạo backup
gmail-bot backup

# Xem danh sách backup
/home/botuser/gmail-bot/backup_production.sh --list

# Restore từ backup
/home/botuser/gmail-bot/backup_production.sh --restore backup_file.tar.gz
```

## 🔒 Security Features

### **Tự động được setup**
- ✅ **UFW Firewall** - Chỉ mở port cần thiết
- ✅ **Fail2ban** - Chống brute force attack
- ✅ **File permissions** - Bảo vệ file nhạy cảm
- ✅ **Service isolation** - Bot chạy với user riêng
- ✅ **Resource limits** - Giới hạn CPU/Memory

### **Manual Security Check**
```bash
# Kiểm tra firewall
sudo ufw status

# Kiểm tra fail2ban
sudo fail2ban-client status

# Kiểm tra permissions
ls -la /home/botuser/gmail-bot/
```

## 📁 Cấu trúc files quan trọng

```
/home/botuser/gmail-bot/
├── config_production.py      # ⚙️ Cấu hình chính
├── credentials.json          # 🔑 Google Service Account
├── gmail_bot.db             # 🗄️ Database SQLite
├── bot.log                  # 📝 Log chính
├── logs/                    # 📂 Thư mục logs
├── backups/                 # 💾 Thư mục backups
├── venv/                    # 🐍 Python virtual environment
├── monitor_production.sh    # 📊 Script monitoring
├── backup_production.sh     # 💾 Script backup
├── bot_manager_production.sh # 🎛️ Script quản lý
└── system_health_check_production.sh # 🏥 Health check
```

## 📚 Tài liệu hướng dẫn

| Tài liệu | Mô tả |
|----------|-------|
| **[COMPLETE_VPS_DEPLOYMENT.md](COMPLETE_VPS_DEPLOYMENT.md)** | 📖 Hướng dẫn deploy chi tiết từng bước |
| **[QUICK_DEPLOYMENT_REFERENCE.md](QUICK_DEPLOYMENT_REFERENCE.md)** | ⚡ Quick reference - Deploy trong 5 phút |
| **[DETAILED_DEPLOYMENT_GUIDE.md](DETAILED_DEPLOYMENT_GUIDE.md)** | 🔧 Hướng dẫn deploy manual |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | 🆘 Khắc phục sự cố thường gặp |

## 🔧 Yêu cầu hệ thống

### **VPS Requirements:**
- **OS**: Ubuntu 20.04 LTS+ (khuyến nghị 22.04)
- **RAM**: Tối thiểu 512MB (khuyến nghị 1GB+)
- **Disk**: 5GB+ trống
- **CPU**: 1 core
- **Network**: Kết nối internet ổn định

### **Chuẩn bị trước khi deploy:**
- 🤖 **Bot Token** từ [@BotFather](https://t.me/BotFather)
- 👤 **Telegram Admin ID** (dùng [@userinfobot](https://t.me/userinfobot))
- 📊 **Google Sheets ID** (tạo Sheet mới)
- 🔑 **Google Service Account JSON** (từ Google Cloud Console)
- 🏦 **Thông tin Bank** (STK, tên ngân hàng)

## 🆘 Troubleshooting

### **Bot không khởi động:**
```bash
# Xem logs lỗi
gmail-bot logs --tail 50

# Kiểm tra cấu hình
gmail-bot config

# Restart service
gmail-bot restart
```

### **Lỗi kết nối API:**
```bash
# Test connectivity
curl -s https://api.telegram.org/bot$BOT_TOKEN/getMe

# Kiểm tra firewall
sudo ufw status
```

### **Database lỗi:**
```bash
# Kiểm tra database
sqlite3 /home/botuser/gmail-bot/gmail_bot.db ".schema"

# Restore từ backup nếu cần
gmail-bot backup
```

## 📞 Hỗ trợ

### **Log Files:**
- Bot logs: `/home/botuser/gmail-bot/logs/`
- System logs: `journalctl -u gmail-bot`
- Monitor logs: `/home/botuser/gmail-bot/logs/monitor.log`

### **Commands for Support:**
```bash
# Tạo report cho support
gmail-bot health > health_report.txt
gmail-bot status > status_report.txt
gmail-bot logs --tail 100 > logs_report.txt
```

## 🎉 Features Ready for Production

- ✅ **24/7 Uptime** với auto-restart
- ✅ **Monitoring tự động** và cảnh báo
- ✅ **Backup tự động** và restore dễ dàng
- ✅ **Security hardening** đầy đủ
- ✅ **Resource optimization** cho VPS nhỏ
- ✅ **Easy management** với CLI tools
- ✅ **Comprehensive logging** và debugging
- ✅ **Health monitoring** và self-healing
- ✅ **Update system** từ GitHub
- ✅ **Production-grade** service management

**🚀 Sẵn sàng cho production! Deploy ngay và bắt đầu kinh doanh!**
| **[VIDEO_DEPLOYMENT_SCRIPT.md](VIDEO_DEPLOYMENT_SCRIPT.md)** | 🎬 Script quay video hướng dẫn deploy |
| **[REPOSITORY_CONFIG.md](REPOSITORY_CONFIG.md)** | 🔧 Cấu hình repository trước deploy |
| **[GITHUB_DEPLOY_GUIDE.md](GITHUB_DEPLOY_GUIDE.md)** | 🚀 Hướng dẫn deploy từ GitHub |
| **[VPS_DEPLOYMENT_GUIDE.md](VPS_DEPLOYMENT_GUIDE.md)** | 🖥️ Hướng dẫn deploy VPS chi tiết |
| **[ADMIN_SETTINGS_GUIDE.md](ADMIN_SETTINGS_GUIDE.md)** | ⚙️ Cấu hình admin settings |
| **[VPS_README.md](VPS_README.md)** | 📖 Quản lý VPS production |
| **[GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md)** | 🔄 Setup CI/CD tự động |
| **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** | 📋 Tổng quan dự án |

## 🛠️ Scripts hỗ trợ

| Script | Chức năng |
|--------|-----------|
| `update_repo_info.sh` | 🔧 Cập nhật thông tin repository |
| `github_deploy.sh` | 🚀 Deploy tự động từ GitHub |
| `auto_update.sh` | 🔄 Cập nhật tự động từ GitHub |
| `quick_deploy.sh` | ⚡ Deploy nhanh one-liner |
| `bot_manager.sh` | 🎛️ Quản lý bot interactive |
| `monitor.sh` | 📊 Monitoring hệ thống |
| `setup_cron.sh` | ⏰ Setup backup và monitoring |

## 🏗️ Kiến trúc hệ thống

```
Gmail Bot Architecture
├── 🤖 Bot Engine (main.py)
├── 👑 Admin Panel (admin_handlers.py)
├── � User Interface (user_handlers.py)
├── ⌨️ Keyboard System (keyboards.py)
├── 🗄️ Database (SQLite + Google Sheets)
├── ⚙️ Settings Manager (Dynamic config)
├── 📊 Monitoring (Health checks)
├── 🔄 Auto-backup (Scheduled tasks)
└── 🚀 Deploy Scripts (Production ready)
```

## 🔒 Tính năng bảo mật

- ✅ **Admin-only functions** - Bảo vệ bằng user ID
- ✅ **Rate limiting** - Chống spam API
- ✅ **Input validation** - Chống SQL injection
- ✅ **Error handling** - Xử lý lỗi an toàn
- ✅ **Credential isolation** - File config riêng biệt
- ✅ **System hardening** - Firewall, SSH security

## 📋 Yêu cầu hệ thống

- **OS**: Ubuntu 20.04 LTS+
- **RAM**: 512MB (khuyến nghị 1GB)
- **Disk**: 2GB trống
- **Python**: 3.9+
- **Network**: Internet ổn định

## 🎯 Production Ready

✅ **Scalable** - Có thể mở rộng  
✅ **Maintainable** - Dễ bảo trì  
✅ **Secure** - Bảo mật cao  
✅ **Reliable** - Hoạt động 24/7  
✅ **Monitored** - Giám sát tự động  
✅ **Automated** - Deploy tự động  

## 🆘 Hỗ trợ

- **📖 Documentation** - Tài liệu đầy đủ
- **🔧 Troubleshooting** - Hướng dẫn sửa lỗi
- **📞 Support** - Hỗ trợ kỹ thuật
- **🐛 Bug Reports** - GitHub Issues

---

**🚀 Sẵn sàng deploy?**

1. **Cập nhật repository info**: `bash update_repo_info.sh your-username/your-repo`
2. **Push lên GitHub**: `git push origin main`
3. **Quick deploy**: `curl -sSL https://raw.githubusercontent.com/your-username/your-repo/main/quick_deploy.sh | sudo bash -s https://github.com/your-username/your-repo.git`

**🎉 Enjoy your Gmail Bot!**

## Cấu trúc dự án
- `main.py` - File chính chạy bot
- `database.py` - Quản lý database SQLite
- `google_sheets.py` - Kết nối Google Sheets
- `config.py` - Cấu hình bot
- `admin_handlers.py` - Xử lý commands admin
- `user_handlers.py` - Xử lý commands user
- `keyboards.py` - Keyboard layouts