# 🔧 HƯỚNG DẪN ADMIN SETTINGS

## ✨ Tính năng mới: Chỉnh sửa cài đặt trực tiếp trên Bot

### 📱 **Cách sử dụng:**

1. **Truy cập Settings:**
   - Nhấn nút `⚙️ Cài đặt` (persistent keyboard)
   - Hoặc sử dụng menu inline → Admin Settings

2. **Các tùy chọn có thể chỉnh sửa:**

   📧 **Thông tin sản phẩm:**
   - `📧 Chỉnh sửa thông tin sản phẩm` - Đổi tên sản phẩm
   
   💰 **Giá cả:**
   - `💰 Chỉnh sửa giá sản phẩm` - Thay đổi giá (VND)
   
   🏦 **Thanh toán:**
   - `🏦 Chỉnh sửa thông tin thanh toán`:
     - Tên ngân hàng
     - Số tài khoản  
     - Tên chủ tài khoản

   📞 **Thông tin liên hệ:**
   - `📞 Chỉnh sửa thông tin liên hệ`:
     - Username admin (hiển thị cho user)
     - Telegram ID admin (để user liên hệ)
     - Giờ hỗ trợ (VD: 8:00 - 22:00)
     - Thời gian phản hồi (VD: 5-15 phút)
     - Cam kết dịch vụ

   👥 **Quản lý user:**
   - `👥 Quản lý User` - Ban/Unban, Cộng tiền cho user, Xem đơn hàng

   💸 **Hệ thống chiết khấu:**
   - Tự động tạo Order ID cho mỗi giao dịch
   - User có thể nhận hoàn tiền theo số lượng email mua
   - Admin có thể theo dõi tất cả đơn hàng và chiết khấu
   - `💸 Chỉnh sửa mức chiết khấu` - Admin thay đổi số tiền hoàn trên từng mức

### 🎯 **Quy trình chỉnh sửa:**

1. **Chọn mục cần sửa** từ menu settings
2. **Nhập thông tin mới** khi bot yêu cầu
3. **Xác nhận** - Bot sẽ lưu và cập nhật ngay lập tức
4. **Áp dụng ngay** - Tất cả chức năng khác sẽ sử dụng thông tin mới

### 💾 **Lưu trữ:**
- Cài đặt được lưu trong file `bot_settings.json`
- Tự động backup khi thay đổi
- Độc lập với file `config.py` gốc

### ⚡ **Tính năng nổi bật:**
- ✅ Thay đổi **ngay lập tức** không cần restart bot
- ✅ **Validation** tự động (kiểm tra định dạng)
- ✅ **Persistent** - Lưu vĩnh viễn
- ✅ **User-friendly** - Giao diện đơn giản
- ✅ **Safe** - Không ảnh hưởng code gốc

### 🔄 **Ví dụ thực tế:**

**Thay đổi giá:**
1. Nhấn `⚙️ Cài đặt` → `💰 Chỉnh sửa giá sản phẩm`
2. Nhập: `10000`  
3. Bot xác nhận: ✅ Đã cập nhật giá: 10,000 VND/email
4. Tất cả giao dịch mới sử dụng giá mới

**Thay đổi thông tin ngân hàng:**
1. `⚙️ Cài đặt` → `🏦 Chỉnh sửa thông tin thanh toán` → `🏦 Chỉnh sửa tên ngân hàng`
2. Nhập: `Vietcombank - Ngân hàng TMCP Ngoại thương Việt Nam`
3. Bot lưu và cập nhật thông tin thanh toán ngay

**Thay đổi thông tin liên hệ:**
1. `⚙️ Cài đặt` → `📞 Chỉnh sửa thông tin liên hệ` → `👤 Chỉnh sửa Username Admin`
2. Nhập: `admin_support`
3. Bot cập nhật username hiển thị cho user ngay lập tức

**Quản lý User:**
1. `👥 Quản lý User` → `💰 Cộng tiền cho User`
2. Nhập User ID: `123456789`
3. Nhập số tiền: `50000`
4. Bot cộng tiền và thông báo cho user

**Xem đơn hàng và chiết khấu:**
1. `👥 Quản lý User` → `📦 Xem tất cả đơn hàng`
2. Xem danh sách đơn hàng với Order ID, số lượng, tổng tiền
3. Theo dõi trạng thái chiết khấu (đã claim/chưa claim)

**Chỉnh sửa mức chiết khấu:**
1. `⚙️ Cài đặt` → `💸 Chỉnh sửa mức chiết khấu`
2. `➕ Thêm/Sửa mức chiết khấu` → Nhập số lượng email → Nhập số tiền hoàn
3. `➖ Xóa mức chiết khấu` → Nhập số lượng email cần xóa
4. `🔄 Khôi phục mặc định` → Khôi phục về cài đặt gốc

---

🎉 **Với tính năng này, admin có thể quản lý toàn diện mà không cần kiến thức kỹ thuật!**

## 🔧 **Các chức năng quản lý khác:**

### 👥 **Quản lý User:**
- **Ban/Unban User:** Khóa/mở khóa tài khoản user
- **Cộng tiền:** Thêm tiền vào tài khoản user (bonus, hoàn tiền, etc.)
- **Xem thông tin:** Theo dõi thông tin user, số dư, lịch sử giao dịch
- **Xem đơn hàng:** Quản lý tất cả đơn hàng với Order ID và trạng thái chiết khấu

### 💸 **Hệ thống chiết khấu mới:**
- **Order ID tự động:** Mỗi giao dịch mua email đều có Order ID duy nhất
- **Bảng mức chiết khấu có thể chỉnh sửa:**
  - Admin có thể thay đổi số tiền hoàn cho từng mức
  - Thêm mức chiết khấu mới (VD: 60 email = hoàn 250,000 VND)
  - Xóa mức chiết khấu không cần thiết
  - Khôi phục về cài đặt mặc định
- **User tự claim:** User sử dụng Order ID để nhận chiết khấu
- **Kiểm soát chặt chẽ:** Mỗi đơn hàng chỉ được claim 1 lần, chỉ chủ đơn hàng mới claim được

### 📞 **Quản lý thông tin liên hệ:**
- **Username Admin:** Hiển thị cho user khi cần hỗ trợ
- **Telegram ID:** User có thể liên hệ trực tiếp
- **Giờ hỗ trợ:** Thông báo thời gian admin online
- **Thời gian phản hồi:** Cam kết thời gian trả lời
- **Cam kết dịch vụ:** Mô tả chất lượng dịch vụ

### 💡 **Lưu ý quan trọng:**
- ✅ Tất cả thay đổi có hiệu lực **ngay lập tức**
- ✅ Không cần restart bot hay chỉnh sửa code
- ✅ Dữ liệu được **backup tự động**
- ✅ Interface thân thiện, dễ sử dụng
- ✅ **Hệ thống Order ID & chiết khấu tự động**
- ✅ **Admin có thể tùy chỉnh mức chiết khấu**
- ⚠️ Chỉ admin mới có quyền truy cập các chức năng này

## 🆔 **Tính năng Order ID & Chiết khấu:**

### 🎯 **Quy trình hoạt động:**
1. **User mua email** → Hệ thống tự động tạo Order ID (VD: ORD12345678)
2. **Hiển thị kết quả** → User nhận email + Order ID + thông báo mức chiết khấu (nếu đủ điều kiện)
3. **User claim chiết khấu** → Vào menu "💸 Chiết khấu" → Nhập Order ID → Nhận tiền ngay
4. **Admin theo dõi** → Xem tất cả đơn hàng, trạng thái chiết khấu trong panel admin

### 💸 **Quản lý mức chiết khấu:**
1. **Xem bảng hiện tại:** `⚙️ Cài đặt` → `💸 Chỉnh sửa mức chiết khấu` → `📊 Xem bảng mức chiết khấu`
2. **Thêm/Sửa mức:** `➕ Thêm/Sửa mức chiết khấu` → Nhập số lượng → Nhập số tiền
3. **Xóa mức:** `➖ Xóa mức chiết khấu` → Nhập số lượng cần xóa
4. **Khôi phục:** `🔄 Khôi phục mặc định` → Về cài đặt gốc

### 📋 **Ví dụ cài đặt mức chiết khấu:**
- **Thêm mức mới:** 15 email → 25,000 VND
- **Sửa mức cũ:** 20 email → 50,000 VND (thay vì 40,000)
- **Xóa mức:** Xóa mức 10 email (không còn chiết khấu cho số lượng nhỏ)

### 🔐 **Bảo mật:**
- ✅ Mỗi Order ID chỉ được sử dụng **1 lần duy nhất**
- ✅ **Chỉ chủ đơn hàng** mới có thể claim chiết khấu
- ✅ **Validation đầy đủ:** Kiểm tra Order ID, User ID, số lượng email
- ✅ **Transaction log:** Tất cả giao dịch chiết khấu đều được ghi lại

## 📊 **Google Sheets Rate Limit & Tối ưu hóa:**

### ⚠️ **Về Rate Limit:**
- **Giới hạn API:** 60 write requests/phút/user
- **Hệ thống bảo vệ:** Tự động delay 2 giây giữa các thao tác
- **Batch size:** Tối đa 3 email/batch để tránh overload
- **Retry logic:** Tự động thử lại sau 45-225 giây nếu bị rate limit

### 🛡️ **Tính năng bảo vệ rate limit:**
1. **Monitoring real-time:** Theo dõi số lượng requests trong cửa sổ 1 phút
2. **Pre-check:** Kiểm tra quota trước khi thực hiện thao tác lớn
3. **Auto-delay:** Tự động chờ khi gần đạt giới hạn
4. **Smart retry:** Tăng thời gian chờ dần cho các lần retry

### 💡 **Khuyến nghị cho Admin:**
- ✅ **Thêm email theo đợt nhỏ:** ≤15 email/lần
- ✅ **Kiểm tra trạng thái:** Dùng menu "📊 Trạng thái Google Sheets"
- ✅ **Chờ đợi kiên nhẫn:** Không thêm email liên tục
- ✅ **Theo dõi quota:** Xem remaining requests trong status
- ⚠️ **Tránh rush hour:** Không thêm hàng trăm email cùng lúc

### 🔧 **Xử lý khi gặp Rate Limit:**
1. **Chờ 2-5 phút** để quota tự reset
2. **Kiểm tra trạng thái** Google Sheets
3. **Thêm email với số lượng nhỏ hơn** (≤9 email)
4. **Sử dụng tính năng batch** tự động của hệ thống

### 📈 **Monitoring & Troubleshooting:**
- **Menu Admin:** `📊 Trạng thái Google Sheets` để xem real-time status
- **Rate limit info:** Hiển thị số requests còn lại và thời gian reset
- **Error handling:** Thông báo chi tiết khi gặp lỗi và cách khắc phục
- **Auto-recovery:** Hệ thống tự động phục hồi sau khi quota reset

## 🛠️ **Troubleshooting & Xử lý sự cố:**

### ⚡ **Bot không phản hồi hoặc lỗi 409 Conflict:**

**Nguyên nhân:** Nhiều instance bot chạy cùng lúc hoặc webhook conflict

**Cách khắc phục:**
1. **Dừng tất cả bot instances:**
   ```bash
   pkill -f "python.*main.py"
   ```

2. **Chờ 5-10 giây** để webhook clear

3. **Khởi động lại bot:**
   ```bash
   python main.py
   ```

4. **Kiểm tra trạng thái:**
   ```bash
   ps aux | grep "python.*main.py"
   ```

### 🔄 **Rate Limit hoặc Google Sheets không phản hồi:**

**Triệu chứng:** Bot báo lỗi "quota exceeded" hoặc không thể thêm email

**Cách xử lý:**
1. **Kiểm tra trạng thái Google Sheets** qua menu admin
2. **Chờ 2-5 phút** để quota reset
3. **Thêm email với batch nhỏ hơn** (≤9 email/lần)
4. **Kiểm tra credentials** Google Sheets nếu lỗi kéo dài

### 💾 **Database hoặc Settings bị lỗi:**

**Triệu chứng:** Bot không lưu cài đặt hoặc mất dữ liệu user

**Cách khắc phục:**
1. **Kiểm tra file permissions:**
   ```bash
   ls -la bot_settings.json database.db
   ```

2. **Backup và khôi phục:**
   - Settings: Copy `bot_settings.json`
   - Database: Copy `database.db`

3. **Reset về mặc định:** Xóa `bot_settings.json` để khôi phục cài đặt gốc

### 🔐 **User không thể sử dụng bot:**

**Nguyên nhân có thể:**
- User bị ban
- Database lỗi
- Bot restart và mất session

**Cách kiểm tra:**
1. **Xem thông tin user** qua menu admin
2. **Kiểm tra trạng thái ban/unban**
3. **Reset user session** bằng cách user gửi `/start`

### 📱 **Keyboard không hiển thị đúng:**

**Cách sửa:**
1. **User gửi `/start`** để refresh keyboard
2. **Admin kiểm tra cài đặt** keyboard trong bot settings
3. **Restart bot** nếu cần thiết

### 🔧 **Emergency Reset:**

**Khi bot bị lỗi nghiêm trọng:**
1. **Backup dữ liệu quan trọng:**
   ```bash
   cp database.db database_backup.db
   cp bot_settings.json settings_backup.json
   ```

2. **Reset bot:**
   ```bash
   pkill -f "python.*main.py"
   rm -f bot_settings.json  # Reset settings
   python main.py
   ```

3. **Cấu hình lại** từ đầu qua menu admin

### 🔧 **Lỗi keyboard functions không tìm thấy:**

**Triệu chứng:** Bot báo lỗi "name 'get_xxx_keyboard' is not defined"

**Nguyên nhân:** Thiếu function keyboard trong file keyboards.py

**Cách khắc phục:**
1. **Kiểm tra log lỗi** để xác định function nào bị thiếu
2. **Tìm function trong backup files** (keyboards_broken.py)
3. **Copy function vào keyboards.py** chính
4. **Restart bot** để áp dụng thay đổi

**Ví dụ lỗi phổ biến:**
- `get_admin_deposit_approval_keyboard` - Keyboard duyệt nạp tiền
- `get_deposit_confirm_keyboard` - Keyboard xác nhận nạp tiền  
- `get_discount_management_keyboard` - Keyboard quản lý chiết khấu

### 📞 **Khi cần hỗ trợ:**

**Thông tin cần cung cấp:**
- Log lỗi cụ thể (copy từ terminal)
- Hành động đang thực hiện khi gặp lỗi
- Thời gian xảy ra lỗi
- User ID gặp vấn đề (nếu có)

**Log files quan trọng:**
- `bot.log` - Log chính của bot
- Terminal output khi chạy `python main.py`
- Error messages trong Telegram

### 📊 **Monitoring và Phân tích Log:**

**Log locations:**
- **Terminal output:** Real-time khi chạy `python main.py`
- **Nohup log:** `bot.log` khi chạy background
- **System log:** `/var/log/` cho system-level issues

**Log levels quan trọng:**
- **INFO:** Hoạt động bình thường (user actions, API calls)
- **WARNING:** Cảnh báo (rate limit, retry attempts)
- **ERROR:** Lỗi cần xử lý (missing functions, API failures)

**Commands hữu ích:**
```bash
# Xem log real-time
tail -f bot.log

# Tìm lỗi trong log
grep "ERROR" bot.log | tail -20

# Xem rate limit issues
grep "quota exceeded\|rate_limit" bot.log

# Monitor bot process
watch "ps aux | grep python.*main.py"
```

**Thống kê từ log:**
- User activity: `grep "from user" bot.log | wc -l`
- Error count: `grep "ERROR" bot.log | wc -l`
- Rate limit events: `grep "Rate limit" bot.log | wc -l`

### 🚀 **Performance Optimization:**

**Bot Performance:**
- **Memory usage:** Typically 50-100MB RAM
- **Response time:** <2s cho most operations
- **Concurrent users:** Supports 50+ simultaneous users
- **Database size:** Optimized for 10k+ users, 100k+ transactions

**Optimization tips:**
1. **Regular cleanup:**
   ```bash
   # Clean old logs
   find . -name "*.log" -mtime +7 -delete
   
   # Compact database periodically  
   sqlite3 database.db "VACUUM;"
   ```

2. **Monitor resource usage:**
   ```bash
   # Check memory usage
   ps aux | grep python | awk '{print $6}'
   
   # Check disk space
   df -h
   ```

3. **Rate limit management:**
   - Keep batch sizes small (≤15 items)
   - Monitor quota usage via admin panel
   - Schedule heavy operations during off-peak hours

### 🎯 **Best Practices cho Admin:**

**Daily Operations:**
- ✅ Kiểm tra trạng thái Google Sheets (morning)
- ✅ Review pending deposits (2-3 times/day)  
- ✅ Monitor error logs (evening)
- ✅ Check user feedback và support requests

**Weekly Maintenance:**
- 🔧 Database vacuum and backup
- 📊 Review performance metrics
- 🔄 Update discount rates nếu cần
- 📈 Analyze sales và user activity

**Monthly Tasks:**
- 💾 Full system backup
- 📋 Review và update admin guide
- 🔐 Security audit (credentials, permissions)
- 📈 Performance analysis và optimization

**Emergency Response:**
- 🚨 Keep backup credentials ready
- 📞 Document escalation procedures  
- 🔄 Test recovery procedures monthly
- 📱 Setup monitoring alerts nếu possible
