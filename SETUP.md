# Hướng dẫn cài đặt Gmail Bot

## Bước 1: Cài đặt Python và dependencies

```bash
# Cài đặt Python packages
pip install -r requirements.txt
```

## Bước 2: Tạo Telegram Bot

1. Nhắn tin cho @BotFather trên Telegram
2. Gửi `/newbot`
3. Đặt tên cho bot
4. Đặt username cho bot (phải kết thúc bằng "bot")
5. Lưu TOKEN nhận được

## Bước 3: Tạo Google Service Account

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Bật Google Sheets API và Google Drive API
4. Tạo Service Account:
   - IAM & Admin > Service Accounts
   - Create Service Account
   - Tải file JSON credentials
5. Đổi tên file thành `credentials.json`

## Bước 4: Tạo Google Sheets

1. Tạo Google Sheets mới
2. Chia sẻ sheet với email service account (từ credentials.json)
3. Thêm header: A1="Email", B1="Password"
4. Copy Sheet ID từ URL (giữa /d/ và /edit)

## Bước 5: Cấu hình Bot

1. Copy `config.py` và chỉnh sửa:
```python
# Bot Token từ BotFather
BOT_TOKEN = "1234567890:ABC..."

# Telegram ID của admin (lấy từ @userinfobot)
ADMIN_IDS = [123456789]

# Thông tin thanh toán
PAYMENT_INFO = {
    "bank_name": "Vietcombank",
    "account_number": "1234567890",
    "account_name": "NGUYEN VAN A",
    "content": "Nap tien {user_id}"
}

# Giá email (VND)
PRODUCT_PRICE = 50000

# Google Sheets ID
GOOGLE_SHEETS_ID = "1ABC...xyz"
```

## Bước 6: Chạy Bot

```bash
python main.py
```

## Lấy Telegram ID

1. Nhắn tin cho @userinfobot
2. Copy User ID
3. Thêm vào ADMIN_IDS trong config.py

## Thêm email vào kho

1. Khởi động bot và gửi /start
2. Chọn "Quản lý Email" > "Thêm email"
3. Gửi danh sách email theo format:
```
email1@gmail.com:password1
email2@gmail.com:password2
```

## Kiểm tra hoạt động

1. Tạo tài khoản user khác
2. Test nạp tiền và mua email
3. Kiểm tra Google Sheets có tự động xóa email

## Lưu ý bảo mật

- Không share credentials.json
- Không commit config.py vào git
- Backup database thường xuyên
- Monitor logs để phát hiện lỗi

## Troubleshooting

### Lỗi Google Sheets
- Kiểm tra credentials.json đúng format
- Kiểm tra service account có quyền truy cập sheet
- Kiểm tra Google Sheets API đã được bật

### Lỗi Telegram
- Kiểm tra BOT_TOKEN đúng
- Bot phải được start bởi user trước khi gửi tin nhắn

### Lỗi Database
- Kiểm tra quyền ghi file trong thư mục
- Backup và restore database nếu cần
