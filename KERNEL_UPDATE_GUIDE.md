# 🔧 **HƯỚNG DẪN UPDATE KERNEL UBUNTU VPS**

## 📋 **KIỂM TRA KERNEL HIỆN TẠI**

### **Xem kernel đang chạy:**
```bash
uname -r
# Output: 5.15.0-113-generic
```

### **Xem các kernel có sẵn:**
```bash
ls /boot/vmlinuz-*
# Xem tất cả kernel đã cài

dpkg --list | grep linux-image
# Xem danh sách kernel packages
```

### **Kiểm tra kernel updates:**
```bash
apt list --upgradable | grep linux
# Xem các updates kernel có sẵn
```

---

## 🚀 **CÁCH UPDATE KERNEL**

### **Method 1: Automatic Update (Khuyến nghị)**
```bash
# 1. Update package list
sudo apt update

# 2. Upgrade tất cả packages (bao gồm kernel)
sudo apt upgrade -y

# 3. Upgrade distribution (nếu cần)
sudo apt dist-upgrade -y

# 4. Cleanup old kernels
sudo apt autoremove -y

# 5. Restart để load kernel mới
sudo reboot
```

### **Method 2: Manual Kernel Update**
```bash
# 1. Tìm kernel packages mới
apt search linux-image-generic

# 2. Install kernel mới cụ thể
sudo apt install linux-image-5.15.0-144-generic linux-headers-5.15.0-144-generic

# 3. Update bootloader
sudo update-grub

# 4. Restart
sudo reboot
```

---

## ⚠️ **TRƯỚC KHI UPDATE - AN TOÀN**

### **1. Backup quan trọng:**
```bash
# Backup cấu hình
sudo cp -r /etc /backup-etc-$(date +%Y%m%d)

# Backup dữ liệu bot (nếu đã cài)
gmail-bot backup 2>/dev/null || true
```

### **2. Kiểm tra disk space:**
```bash
df -h
# Cần ít nhất 1GB trống cho kernel mới
```

### **3. Check running services:**
```bash
systemctl list-units --state=running
# Note các service quan trọng
```

---

## 🔄 **QUY TRÌNH UPDATE AN TOÀN**

### **Step 1: Preparation**
```bash
# Update package list
sudo apt update

# Check available updates
apt list --upgradable

# Free up space if needed
sudo apt autoremove -y
sudo apt autoclean
```

### **Step 2: Backup (Quan trọng!)**
```bash
# Tạo snapshot nếu provider hỗ trợ
# Hoặc backup files quan trọng
sudo tar -czf /tmp/system-backup-$(date +%Y%m%d).tar.gz /etc /home
```

### **Step 3: Update Kernel**
```bash
# Full system upgrade
sudo apt upgrade -y

# Distribution upgrade (for kernel)
sudo apt dist-upgrade -y

# Update bootloader
sudo update-grub
```

### **Step 4: Clean up**
```bash
# Remove old kernels (keep 2-3 latest)
sudo apt autoremove -y

# Clean package cache
sudo apt autoclean
```

### **Step 5: Restart**
```bash
# Schedule restart (optional)
sudo shutdown -r +5 "System will restart in 5 minutes for kernel update"

# Or restart immediately
sudo reboot
```

---

## ✅ **SAU KHI RESTART**

### **Verify kernel update:**
```bash
# Check new kernel version
uname -r
# Should show: 5.15.0-144-generic

# Check system info
hostnamectl

# Check boot log
dmesg | head -20
```

### **Check services:**
```bash
# Check all services
systemctl --failed

# Check specific service (if bot installed)
systemctl status gmail-bot
```

### **Performance check:**
```bash
# Memory usage
free -h

# Load average
uptime

# Disk usage
df -h
```

---

## 🆘 **TROUBLESHOOTING**

### **Nếu system không boot:**
```bash
# Boot vào kernel cũ từ GRUB menu
# Thường có option "Advanced options" > chọn kernel cũ

# Sau khi boot thành công với kernel cũ:
sudo apt remove linux-image-5.15.0-144-generic
sudo update-grub
```

### **Nếu có lỗi dependencies:**
```bash
# Fix broken packages
sudo apt --fix-broken install

# Reconfigure packages
sudo dpkg --configure -a

# Force update
sudo apt dist-upgrade --fix-missing
```

### **Recovery mode:**
```bash
# Boot vào recovery mode từ GRUB
# Chọn "Drop to root shell prompt"
# Fix issues manually
```

---

## 🛡️ **BEST PRACTICES**

### **1. Timing:**
- ⏰ **Update khi ít traffic** (đêm/sáng sớm)
- 📅 **Lên lịch trước** cho users
- ⚡ **Maintenance window** rõ ràng

### **2. Testing:**
- 🧪 **Test trên staging** trước
- 📊 **Monitor performance** sau update
- 🔄 **Rollback plan** sẵn sàng

### **3. Documentation:**
- 📝 **Ghi log** quá trình update
- 💾 **Backup configs** quan trọng
- 📞 **Contact support** nếu cần

---

## 🎯 **QUICK UPDATE COMMAND**

### **Nếu muốn update nhanh:**
```bash
# One-liner update (cẩn thận!)
sudo apt update && sudo apt upgrade -y && sudo apt dist-upgrade -y && sudo apt autoremove -y && sudo reboot
```

### **Hoặc từng bước an toàn:**
```bash
# Step by step
sudo apt update
sudo apt upgrade -y
sudo apt dist-upgrade -y
sudo apt autoremove -y
sudo reboot
```

---

## ⚡ **SAU UPDATE - BOT SETUP**

Nếu bạn update kernel trước khi cài bot:
```bash
# Deploy bot sau khi kernel mới
curl -sSL https://raw.githubusercontent.com/TvyAZ/mailnige/main/production_deploy.sh | sudo bash -s -- https://github.com/TvyAZ/mailnige.git
```

Nếu bot đã cài, kiểm tra sau restart:
```bash
gmail-bot status
gmail-bot health
```

**💡 Tip**: Kernel update thường rất an toàn trên Ubuntu LTS, nhưng luôn backup trước!
