# Cấu hình bot Telegram
BOT_TOKEN = "7794665161:AAH1aP1udD7ARCqrI5-PJP57uY4kNUiJsTo"

# ID admin (thay bằng Telegram ID của bạn)
ADMIN_IDS = [890641298]  # Thêm ID admin vào đây

# Cấu hình thanh toán
PAYMENT_INFO = {
    "bank_name": "TPBank- Ngân hàng TMCP Tiên Phong",
    "account_number": "8328 6868 886",
    "account_name": "NGUYEN THI THUY VY",
    "content": "botmail {user_id}"
}

# Cấu hình sản phẩm
PRODUCT_PRICE = 5000  # Giá 1 email (VND)

# Cấu hình Google Sheets
GOOGLE_SHEETS_ID = "1i2sZttHrpTgR2dg3rbJbUybwlqiE4oUkuSOJXPUoj0o"
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# Database
DATABASE_FILE = "gmail_bot.db"

# Messages
MESSAGES = {
    "welcome": """🤖 **BOT BÁN GMAIL NIGERIA TỰ ĐỘNG**

📧 **Sản phẩm:** Gmail Nigeria
Gmail được người dân Nigeria đăng ký thủ công

🌍 Tạo bằng IP Nigeria chuẩn, độ trust cao

💼 Phù hợp sử dụng cho app thanh toán, verify, Google Voice,...

🔐 **CHÍNH SÁCH BẢO HÀNH**
⏰ Thời hạn bảo hành: 24h kể từ khi đơn hàng được gửi đi

✅ **Bảo hành các trường hợp:**
• Không đăng nhập được lần đầu
• Sai mật khẩu
• Bị yêu cầu verify SĐT
• Không đúng IP Nigeria

🛑 **Hết bảo hành khi:**
• Login lần đầu thành công
• IP gốc login là IP Nigeria chuẩn

🔄 **Phương án bảo hành:** 1 đổi 1
👉 Liên hệ Admin để xử lý bảo hành

💡 **LƯU Ý KHI SỬ DỤNG**
❌ Không đăng nhập Gmail bằng giả lập
✅ Nên login lần đầu bằng IP Việt Nam, sau đó mới chuyển IP Nigeria

🔁 **Trick dùng cho S9 MiChange:**
• Login lần đầu bằng IP Việt Nam
• Đóng tab Google Play
• Bật proxy → kiểm tra IP tại ipx.ac
• Mở lại Google Play → vào app thanh toán

💰 **CHÍNH SÁCH HOÀN TIỀN**
• Bot không có chức năng rút tiền
• Trường hợp bot dừng hoạt động, Admin sẽ thông báo
• Người dùng có thể liên hệ Admin để được hoàn tiền thủ công (theo dữ liệu giao dịch gần nhất từ bot)

🎁 **CHIẾT KHẤU SỈ**
• Có chiết khấu tốt dành cho người mua số lượng lớn
• Inbox Admin để nhận bảng giá & ưu đãi chi tiết

📩 Liên hệ Admin để mua hàng, hỗ trợ và bảo hành
⚡ **Tự động – Nhanh chóng – An toàn – Minh bạch**""",
    "admin_welcome": "👑 Chào Admin! Chọn chức năng quản lý:",
    "user_welcome": "👤 Chào bạn! Chọn chức năng:",
}
