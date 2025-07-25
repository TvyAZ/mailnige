"""
Dynamic Settings Manager - Quản lý cài đặt có thể thay đổi
"""
import json
import os
from config import PRODUCT_PRICE, PAYMENT_INFO

SETTINGS_FILE = "bot_settings.json"

# Cài đặt mặc định
DEFAULT_SETTINGS = {
    "product_price": PRODUCT_PRICE,
    "product_name": "Email Gmail",
    "product_description": "Gmail mới, chưa sử dụng, chất lượng cao",
    "payment_info": {
        "bank_name": PAYMENT_INFO["bank_name"],
        "account_number": PAYMENT_INFO["account_number"],
        "account_name": PAYMENT_INFO["account_name"],
        "content": PAYMENT_INFO["content"]
    },
    "contact_info": {
        "admin_username": "@admin_support",
        "admin_telegram_id": "890641298",
        "support_hours": "24/7",
        "response_time": "Phản hồi nhanh trong 5 phút!",
        "commitment": "Cam kết hỗ trợ tận tình!"
    },
    "discount_rates": {
        "10": 10000,   # 10 email = hoàn 10,000 VND
        "20": 40000,   # 20 email = hoàn 40,000 VND
        "30": 70000,   # 30 email = hoàn 70,000 VND
        "40": 105000,  # 40 email = hoàn 105,000 VND
        "50": 170000   # 50 email = hoàn 170,000 VND
    }
}

class SettingsManager:
    def __init__(self):
        self.settings_file = SETTINGS_FILE
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Tải cài đặt từ file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Lỗi tải cài đặt: {e}")
                return DEFAULT_SETTINGS.copy()
        else:
            # Tạo file cài đặt mặc định
            self.save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
    
    def save_settings(self, settings=None):
        """Lưu cài đặt vào file"""
        if settings is None:
            settings = self.settings
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Lỗi lưu cài đặt: {e}")
            return False
    
    def get_product_price(self):
        """Lấy giá sản phẩm"""
        return self.settings.get("product_price", DEFAULT_SETTINGS["product_price"])
    
    def set_product_price(self, price):
        """Đặt giá sản phẩm"""
        self.settings["product_price"] = int(price)
        return self.save_settings()
    
    def get_product_name(self):
        """Lấy tên sản phẩm"""
        return self.settings.get("product_name", DEFAULT_SETTINGS["product_name"])
    
    def set_product_name(self, name):
        """Đặt tên sản phẩm"""
        self.settings["product_name"] = str(name)
        return self.save_settings()
    
    def get_product_description(self):
        """Lấy mô tả sản phẩm"""
        return self.settings.get("product_description", DEFAULT_SETTINGS["product_description"])
    
    def set_product_description(self, description):
        """Đặt mô tả sản phẩm"""
        self.settings["product_description"] = str(description)
        return self.save_settings()
    
    def get_payment_info(self):
        """Lấy thông tin thanh toán"""
        return self.settings.get("payment_info", DEFAULT_SETTINGS["payment_info"])
    
    def set_bank_name(self, bank_name):
        """Đặt tên ngân hàng"""
        if "payment_info" not in self.settings:
            self.settings["payment_info"] = DEFAULT_SETTINGS["payment_info"].copy()
        self.settings["payment_info"]["bank_name"] = str(bank_name)
        return self.save_settings()
    
    def set_account_number(self, account_number):
        """Đặt số tài khoản"""
        if "payment_info" not in self.settings:
            self.settings["payment_info"] = DEFAULT_SETTINGS["payment_info"].copy()
        self.settings["payment_info"]["account_number"] = str(account_number)
        return self.save_settings()
    
    def set_account_name(self, account_name):
        """Đặt tên chủ tài khoản"""
        if "payment_info" not in self.settings:
            self.settings["payment_info"] = DEFAULT_SETTINGS["payment_info"].copy()
        self.settings["payment_info"]["account_name"] = str(account_name)
        return self.save_settings()
    
    # ==================== CONTACT INFO MANAGEMENT ====================
    
    def get_contact_info(self):
        """Lấy thông tin liên hệ"""
        return self.settings.get("contact_info", DEFAULT_SETTINGS["contact_info"])
    
    def set_admin_username(self, username):
        """Đặt username admin"""
        if "contact_info" not in self.settings:
            self.settings["contact_info"] = DEFAULT_SETTINGS["contact_info"].copy()
        # Đảm bảo username có @ ở đầu
        if not username.startswith('@'):
            username = '@' + username
        self.settings["contact_info"]["admin_username"] = str(username)
        return self.save_settings()
    
    def set_admin_telegram_id(self, telegram_id):
        """Đặt Telegram ID admin"""
        if "contact_info" not in self.settings:
            self.settings["contact_info"] = DEFAULT_SETTINGS["contact_info"].copy()
        self.settings["contact_info"]["admin_telegram_id"] = str(telegram_id)
        return self.save_settings()
    
    def set_support_hours(self, hours):
        """Đặt giờ hỗ trợ"""
        if "contact_info" not in self.settings:
            self.settings["contact_info"] = DEFAULT_SETTINGS["contact_info"].copy()
        self.settings["contact_info"]["support_hours"] = str(hours)
        return self.save_settings()
    
    def set_response_time(self, response_time):
        """Đặt thời gian phản hồi"""
        if "contact_info" not in self.settings:
            self.settings["contact_info"] = DEFAULT_SETTINGS["contact_info"].copy()
        self.settings["contact_info"]["response_time"] = str(response_time)
        return self.save_settings()
    
    def set_commitment(self, commitment):
        """Đặt cam kết hỗ trợ"""
        if "contact_info" not in self.settings:
            self.settings["contact_info"] = DEFAULT_SETTINGS["contact_info"].copy()
        self.settings["contact_info"]["commitment"] = str(commitment)
        return self.save_settings()
    
    def get_contact_message(self):
        """Tạo message liên hệ từ settings"""
        contact_info = self.get_contact_info()
        payment_info = self.get_payment_info()
        
        message = f"""📞 THÔNG TIN LIÊN HỆ ADMIN

👤 Admin: {contact_info['admin_username']}
📱 Telegram ID: {contact_info['admin_telegram_id']}
💬 Hỗ trợ: {contact_info['support_hours']}

🏦 THÔNG TIN THANH TOÁN:
• Bank: {payment_info['bank_name']}
• STK: {payment_info['account_number']}
• Tên: {payment_info['account_name']}

⚡ {contact_info['response_time']}
🛡️ {contact_info['commitment']}"""
        
        return message
    
    def get_all_settings(self):
        """Lấy tất cả cài đặt"""
        return self.settings.copy()
    
    def reset_to_default(self):
        """Reset về cài đặt mặc định"""
        self.settings = DEFAULT_SETTINGS.copy()
        return self.save_settings()
    
    # ==================== DISCOUNT RATES MANAGEMENT ====================
    
    def get_discount_rates(self):
        """Lấy bảng mức chiết khấu"""
        return self.settings.get("discount_rates", DEFAULT_SETTINGS["discount_rates"])
    
    def set_discount_rate(self, email_quantity, discount_amount):
        """Đặt mức chiết khấu cho số lượng email cụ thể"""
        if "discount_rates" not in self.settings:
            self.settings["discount_rates"] = DEFAULT_SETTINGS["discount_rates"].copy()
        
        self.settings["discount_rates"][str(email_quantity)] = int(discount_amount)
        return self.save_settings()
    
    def remove_discount_rate(self, email_quantity):
        """Xóa mức chiết khấu cho số lượng email cụ thể"""
        if "discount_rates" not in self.settings:
            self.settings["discount_rates"] = DEFAULT_SETTINGS["discount_rates"].copy()
        
        if str(email_quantity) in self.settings["discount_rates"]:
            del self.settings["discount_rates"][str(email_quantity)]
            return self.save_settings()
        return False
    
    def get_discount_amount(self, email_quantity):
        """Tính số tiền chiết khấu theo số lượng email"""
        discount_rates = self.get_discount_rates()
        
        # Tìm mức chiết khấu cao nhất mà user đủ điều kiện
        max_discount = 0
        for quantity_str, discount in discount_rates.items():
            quantity = int(quantity_str)
            if email_quantity >= quantity:
                max_discount = max(max_discount, discount)
        
        return max_discount
    
    def get_discount_info_text(self):
        """Lấy text hiển thị bảng mức chiết khấu"""
        discount_rates = self.get_discount_rates()
        
        if not discount_rates:
            return "Hiện tại chưa có chương trình chiết khấu nào."
        
        text = "📊 **BẢNG MỨC CHIẾT KHẤU**\n\n💰 **Mức hoàn tiền theo số lượng email:**\n\n"
        
        # Sắp xếp theo số lượng email
        sorted_rates = sorted(discount_rates.items(), key=lambda x: int(x[0]))
        
        icons = ["🥉", "🥈", "🥇", "💎", "👑"]
        for i, (quantity, discount) in enumerate(sorted_rates):
            icon = icons[i] if i < len(icons) else "⭐"
            text += f"{icon} **{quantity} email** → Hoàn **{discount:,} VND**\n"
        
        return text

# Khởi tạo instance global
settings_manager = SettingsManager()
