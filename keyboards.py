from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard(is_admin=False):
    """Keyboard chính cho user và admin"""
    if is_admin:
        keyboard = [
            [InlineKeyboardButton("📊 Thống kê", callback_data="admin_stats")],
            [InlineKeyboardButton("📧 Quản lý Email", callback_data="admin_emails"),
             InlineKeyboardButton("👥 Quản lý User", callback_data="admin_users")],
            [InlineKeyboardButton("💰 Duyệt nạp tiền", callback_data="admin_deposits"),
             InlineKeyboardButton("⚙️ Cài đặt", callback_data="admin_settings")],
            [InlineKeyboardButton("👤 Chế độ User", callback_data="user_mode")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("💳 Nạp tiền", callback_data="user_deposit")],
            [InlineKeyboardButton("📧 Mua Email", callback_data="user_buy_email")],
            [InlineKeyboardButton("👤 Tài khoản", callback_data="user_account"),
             InlineKeyboardButton("💸 Chiết khấu", callback_data="user_discount")],
            [InlineKeyboardButton("📞 Liên hệ", callback_data="user_contact")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

def get_admin_emails_keyboard():
    """Keyboard quản lý email admin"""
    keyboard = [
        [InlineKeyboardButton("📋 Xem kho email", callback_data="admin_view_emails")],
        [InlineKeyboardButton("➕ Thêm email", callback_data="admin_add_emails")],
        [InlineKeyboardButton("� Trạng thái Google Sheets", callback_data="admin_sheets_status")],
        [InlineKeyboardButton("�🔙 Quay lại", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_users_keyboard():
    """Keyboard quản lý user admin"""
    keyboard = [
        [InlineKeyboardButton("👥 Danh sách User", callback_data="admin_list_users")],
        [InlineKeyboardButton("🚫 Ban/Unban User", callback_data="admin_ban_user")],
        [InlineKeyboardButton("💰 Cộng tiền User", callback_data="admin_add_balance")],
        [InlineKeyboardButton("📦 Xem tất cả đơn hàng", callback_data="admin_view_orders")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_account_keyboard():
    """Keyboard tài khoản user"""
    keyboard = [
        [InlineKeyboardButton("💰 Xem số dư", callback_data="user_balance")],
        [InlineKeyboardButton("📜 Lịch sử giao dịch", callback_data="user_transactions")],
        [InlineKeyboardButton("📧 Email đã mua", callback_data="user_purchases")],
        [InlineKeyboardButton("📦 Đơn hàng của tôi", callback_data="user_orders")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="user_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_deposit_keyboard():
    """Keyboard nạp tiền"""
    keyboard = [
        [InlineKeyboardButton("💰 Nạp 50,000 VND", callback_data="deposit_50000")],
        [InlineKeyboardButton("💰 Nạp 100,000 VND", callback_data="deposit_100000")],
        [InlineKeyboardButton("💰 Nạp 200,000 VND", callback_data="deposit_200000")],
        [InlineKeyboardButton("💰 Nạp 500,000 VND", callback_data="deposit_500000")],
        [InlineKeyboardButton("📝 Số tiền khác", callback_data="deposit_custom")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="user_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_deposit_keyboard(amount):
    """Keyboard xác nhận nạp tiền"""
    keyboard = [
        [InlineKeyboardButton("✅ Đã chuyển tiền", callback_data=f"deposit_confirm_{amount}")],
        [InlineKeyboardButton("❌ Hủy", callback_data="user_deposit")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_deposit_keyboard():
    """Keyboard duyệt nạp tiền admin"""
    keyboard = [
        [InlineKeyboardButton("📋 Xem yêu cầu nạp tiền", callback_data="admin_pending_deposits")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_buy_email_keyboard():
    """Keyboard mua email"""
    keyboard = [
        [InlineKeyboardButton("📧 Mua 1 Email", callback_data="buy_email_1")],
        [InlineKeyboardButton("📧📧 Mua 2 Email", callback_data="buy_email_2")],
        [InlineKeyboardButton("📧📧📧 Mua 3 Email", callback_data="buy_email_3")],
        [InlineKeyboardButton("📧📧📧📧📧 Mua 5 Email", callback_data="buy_email_5")],
        [InlineKeyboardButton("💰 Số lượng khác", callback_data="buy_email_custom")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="user_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_purchase_keyboard(quantity, total_price):
    """Keyboard xác nhận mua email"""
    keyboard = [
        [InlineKeyboardButton("✅ Xác nhận mua", callback_data=f"confirm_purchase_{quantity}_{total_price}")],
        [InlineKeyboardButton("❌ Hủy", callback_data="user_buy_email")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(callback_data="user_back"):
    """Keyboard quay lại"""
    keyboard = [
        [InlineKeyboardButton("🔙 Quay lại", callback_data=callback_data)]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_pagination_keyboard(page, total_pages, prefix="page"):
    """Keyboard phân trang"""
    keyboard = []
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Trước", callback_data=f"{prefix}_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Sau ➡️", callback_data=f"{prefix}_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 Quay lại", callback_data="admin_back")])
    
    return InlineKeyboardMarkup(keyboard)

def get_user_action_keyboard(user_id):
    """Keyboard hành động với user"""
    keyboard = [
        [InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_user_{user_id}"),
         InlineKeyboardButton("✅ Unban User", callback_data=f"unban_user_{user_id}")],
        [InlineKeyboardButton("💰 Cộng tiền", callback_data=f"add_balance_{user_id}")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="admin_users")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_persistent_keyboard_user():
    """Persistent reply keyboard cho user"""
    keyboard = [
        ["💳 Nạp tiền", "📧 Mua Email"],
        ["👤 Tài khoản", "💸 Chiết khấu"],
        ["📞 Liên hệ", "📋 Menu"]
    ]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=False,
        input_field_placeholder="Chọn chức năng..."
    )

def get_persistent_keyboard_admin():
    """Persistent reply keyboard cho admin"""
    keyboard = [
        ["📊 Thống kê", "📧 Quản lý Email"],
        ["👥 Quản lý User", "💰 Duyệt nạp tiền"],
        ["⚙️ Cài đặt", "👤 Chế độ User"]
    ]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=False,
        input_field_placeholder="Chọn chức năng admin..."
    )

def get_empty_keyboard():
    """Keyboard rỗng để ẩn keyboard"""
    return ReplyKeyboardMarkup([[]], resize_keyboard=True, one_time_keyboard=True)

def get_admin_settings_keyboard():
    """Keyboard cài đặt admin với các tùy chọn chỉnh sửa"""
    keyboard = [
        [InlineKeyboardButton("💰 Chỉnh sửa giá sản phẩm", callback_data="admin_edit_price")],
        [InlineKeyboardButton("🏦 Chỉnh sửa thông tin thanh toán", callback_data="admin_edit_payment")],
        [InlineKeyboardButton("📧 Chỉnh sửa thông tin sản phẩm", callback_data="admin_edit_product")],
        [InlineKeyboardButton("📞 Chỉnh sửa thông tin liên hệ", callback_data="admin_edit_contact")],
        [InlineKeyboardButton("💸 Chỉnh sửa mức chiết khấu", callback_data="admin_edit_discount")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_payment_keyboard():
    """Keyboard chỉnh sửa thông tin thanh toán"""
    keyboard = [
        [InlineKeyboardButton("🏦 Chỉnh sửa tên ngân hàng", callback_data="admin_edit_bank_name")],
        [InlineKeyboardButton("💳 Chỉnh sửa số tài khoản", callback_data="admin_edit_account_number")],
        [InlineKeyboardButton("👤 Chỉnh sửa tên chủ tài khoản", callback_data="admin_edit_account_name")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="admin_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_contact_keyboard():
    """Keyboard chỉnh sửa thông tin liên hệ"""
    keyboard = [
        [InlineKeyboardButton("👤 Chỉnh sửa username admin", callback_data="admin_edit_username")],
        [InlineKeyboardButton("📱 Chỉnh sửa Telegram ID", callback_data="admin_edit_telegram_id")],
        [InlineKeyboardButton("🕒 Chỉnh sửa giờ hỗ trợ", callback_data="admin_edit_support_hours")],
        [InlineKeyboardButton("⚡ Chỉnh sửa thời gian phản hồi", callback_data="admin_edit_response_time")],
        [InlineKeyboardButton("🛡️ Chỉnh sửa cam kết hỗ trợ", callback_data="admin_edit_commitment")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="admin_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_discount_keyboard():
    """Keyboard chiết khấu user"""
    keyboard = [
        [InlineKeyboardButton("💸 Nhận chiết khấu", callback_data="user_claim_discount")],
        [InlineKeyboardButton("📊 Bảng mức chiết khấu", callback_data="user_discount_rates")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="user_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_discount_keyboard():
    """Keyboard chỉnh sửa mức chiết khấu"""
    keyboard = [
        [InlineKeyboardButton("📊 Xem bảng mức chiết khấu", callback_data="admin_view_discount_rates")],
        [InlineKeyboardButton("➕ Thêm/Sửa mức chiết khấu", callback_data="admin_add_discount_rate")],
        [InlineKeyboardButton("➖ Xóa mức chiết khấu", callback_data="admin_remove_discount_rate")],
        [InlineKeyboardButton("🔄 Khôi phục mặc định", callback_data="admin_reset_discount_rates")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="admin_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_persistent_user_keyboard():
    """Persistent keyboard cho user"""
    keyboard = [
        [KeyboardButton("💳 Nạp tiền"), KeyboardButton("📧 Mua Email")],
        [KeyboardButton("👤 Tài khoản"), KeyboardButton("💸 Chiết khấu")],
        [KeyboardButton("📞 Liên hệ")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, persistent=True)

def get_admin_deposit_approval_keyboard(transaction_id):
    """Keyboard duyệt nạp tiền admin"""
    keyboard = [
        [InlineKeyboardButton("✅ Duyệt", callback_data=f"approve_deposit_{transaction_id}"),
         InlineKeyboardButton("❌ Từ chối", callback_data=f"reject_deposit_{transaction_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)
