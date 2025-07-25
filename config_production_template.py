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

# Security
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
