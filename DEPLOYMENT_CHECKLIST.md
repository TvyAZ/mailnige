# 📋 **CHECKLIST DEPLOY VPS UBUNTU - GMAIL BOT**

## ✅ **CHUẨN BỊ TRƯỚC KHI DEPLOY**

### **1. Thông tin cần có sẵn:**
- [ ] 🤖 **Bot Token** từ [@BotFather](https://t.me/BotFather)
- [ ] 👤 **Telegram Admin ID** (dùng [@userinfobot](https://t.me/userinfobot))
- [ ] 📊 **Google Sheets ID** (tạo Sheet mới trên Google Drive)
- [ ] 🔑 **Google Service Account JSON** (từ Google Cloud Console)
- [ ] 🏦 **Thông tin Bank** (STK, tên ngân hàng, tên chủ TK)

### **2. VPS chuẩn bị:**
- [ ] ✅ **Ubuntu 20.04+** đã cài đặt
- [ ] ✅ **Root access** qua SSH
- [ ] ✅ **Internet connection** ổn định
- [ ] ✅ **512MB+ RAM** available
- [ ] ✅ **5GB+ disk space** trống

---

## 🚀 **DEPLOY TỰ ĐỘNG (KHUYẾN NGHỊ)**

### **Bước 1: Kết nối VPS**
```bash
ssh root@your-vps-ip
```

### **Bước 2: Chạy lệnh deploy tự động**
```bash
# Thay your-username/mailnige bằng repository thật
curl -sSL https://raw.githubusercontent.com/your-username/mailnige/main/production_deploy.sh | sudo bash -s -- https://github.com/your-username/mailnige.git
```

### **Bước 3: Kiểm tra deployment**
```bash
gmail-bot status
```

---

## ⚙️ **CẤU HÌNH BOT**

### **1. Cấu hình chính**
```bash
nano /home/botuser/gmail-bot/config_production.py
```

**Cần thay đổi:**
- `BOT_TOKEN = "your_bot_token_here"`
- `ADMIN_ID = 123456789`
- `GOOGLE_SHEETS_ID = "your_google_sheets_id_here"`
- `BANK_INFO` (thông tin ngân hàng)

### **2. Upload Google Credentials**
```bash
nano /home/botuser/gmail-bot/credentials.json
# Paste nội dung file JSON từ Google Cloud Console
```

### **3. Kiểm tra cấu hình**
```bash
gmail-bot config
```

---

## 🏃 **KHỞI ĐỘNG VÀ KIỂM TRA**

### **1. Khởi động bot**
```bash
gmail-bot start
```

### **2. Kiểm tra trạng thái**
```bash
gmail-bot status
```

### **3. Xem logs**
```bash
gmail-bot logs -f
# Ctrl+C để thoát
```

### **4. Health check toàn diện**
```bash
gmail-bot health
```

---

## ✅ **CHECKLIST HOÀN THÀNH**

### **Deploy Process:**
- [ ] ✅ System packages updated
- [ ] ✅ Bot user created
- [ ] ✅ Virtual environment setup
- [ ] ✅ Dependencies installed
- [ ] ✅ Service file created
- [ ] ✅ Monitoring setup
- [ ] ✅ Backup system configured
- [ ] ✅ Security hardened
- [ ] ✅ Log rotation setup

### **Configuration:**
- [ ] ✅ Bot token configured
- [ ] ✅ Admin ID set
- [ ] ✅ Google Sheets ID set
- [ ] ✅ Google credentials uploaded
- [ ] ✅ Bank information configured

### **Services:**
- [ ] ✅ Bot service running
- [ ] ✅ Auto-restart enabled
- [ ] ✅ Monitoring active
- [ ] ✅ Backup scheduled
- [ ] ✅ Firewall configured
- [ ] ✅ Fail2ban active

### **Testing:**
- [ ] ✅ Bot responds to /start
- [ ] ✅ Admin commands working
- [ ] ✅ Database operations OK
- [ ] ✅ Google Sheets connection OK
- [ ] ✅ No errors in logs

---

## 🎮 **LỆNH QUẢN LÝ THƯỜNG DÙNG**

```bash
# Quản lý cơ bản
gmail-bot start      # Khởi động
gmail-bot stop       # Dừng
gmail-bot restart    # Khởi động lại
gmail-bot status     # Trạng thái

# Monitoring
gmail-bot logs       # Xem logs
gmail-bot logs -f    # Theo dõi logs real-time
gmail-bot health     # Health check

# Maintenance
gmail-bot backup     # Tạo backup
gmail-bot update     # Update từ GitHub
gmail-bot cleanup    # Dọn dẹp files cũ
```

---

## 🔄 **AUTOMATED FEATURES ĐANG HOẠT ĐỘNG**

### **Monitoring (mỗi 5 phút):**
- ✅ Check service status
- ✅ Monitor memory/CPU usage
- ✅ Check API connectivity
- ✅ Auto-restart if needed

### **Backup (mỗi 6 giờ):**
- ✅ Database backup
- ✅ Configuration backup
- ✅ Log files backup
- ✅ Cleanup old backups

### **Health Check (mỗi giờ):**
- ✅ System health monitoring
- ✅ Auto-fix minor issues
- ✅ Security checks
- ✅ Performance monitoring

### **Security:**
- ✅ UFW Firewall active
- ✅ Fail2ban protection
- ✅ Log rotation
- ✅ File permissions secured

---

## 🆘 **TROUBLESHOOTING NHANH**

### **Bot không khởi động:**
```bash
gmail-bot logs --tail 20
gmail-bot health --fix
```

### **Lỗi cấu hình:**
```bash
gmail-bot config
nano /home/botuser/gmail-bot/config_production.py
```

### **Lỗi Google Sheets:**
```bash
ls -la /home/botuser/gmail-bot/credentials.json
gmail-bot health
```

### **Bot crash liên tục:**
```bash
journalctl -u gmail-bot --no-pager -n 50
gmail-bot restart
```

---

## 🎉 **DEPLOYMENT HOÀN TẤT!**

✅ **Bot đã sẵn sàng hoạt động 24/7**
✅ **Monitoring tự động đang chạy**
✅ **Backup được lên lịch**
✅ **Security được cường hóa**
✅ **Quản lý dễ dàng qua CLI**

**🚀 Chúc mừng! Bot Gmail Telegram của bạn đã production-ready!**
