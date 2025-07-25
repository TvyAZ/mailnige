import logging
import asyncio
from telegram import Update, MenuButton, MenuButtonCommands, MenuButtonWebApp, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database import Database
from google_sheets import GoogleSheetsManager
from keyboards import *
from config import *
from admin_handlers import *
from user_handlers import *
from settings_manager import settings_manager

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GmailBot:
    def __init__(self):
        self.db = Database(DATABASE_FILE)
        
        # Khởi tạo Google Sheets nếu có thể
        try:
            self.sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
            self.sheets.setup_sheet_headers()
            logger.info("Đã kết nối Google Sheets thành công")
        except Exception as e:
            logger.error(f"Lỗi kết nối Google Sheets: {e}")
            self.sheets = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /start"""
        user = update.effective_user
        user_id = user.id
        
        # Kiểm tra user bị ban
        if self.db.is_user_banned(user_id):
            await update.message.reply_text("🚫 **Tài khoản của bạn đã bị khóa!**\n\n📞 Liên hệ admin để được hỗ trợ.", parse_mode='Markdown')
            return
        
        # Thêm user vào database
        self.db.add_user(user_id, user.username, user.first_name)
        
        # Kiểm tra admin
        is_admin = user_id in ADMIN_IDS
        
        welcome_message = MESSAGES["admin_welcome"] if is_admin else MESSAGES["welcome"] + "\n\n" + MESSAGES["user_welcome"]
        
        # Sử dụng persistent keyboard thay vì inline keyboard
        is_admin = user_id in ADMIN_IDS
        if is_admin:
            keyboard = get_persistent_keyboard_admin()
        else:
            keyboard = get_persistent_keyboard_user()
        
        await update.message.reply_text(welcome_message, reply_markup=keyboard, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /help"""
        help_text = """🤖 **HƯỚNG DẪN SỬ DỤNG BOT**

**👤 Dành cho User:**
• `/start` - Khởi động bot
• `💳 Nạp tiền` - Nạp tiền vào tài khoản
• `📧 Mua Email` - Mua email Gmail
• `👤 Tài khoản` - Xem thông tin tài khoản
• `📞 Liên hệ` - Thông tin liên hệ admin

**📧 Quy trình mua email:**
1. Nạp tiền vào tài khoản
2. Chọn "Mua Email"
3. Chọn số lượng
4. Xác nhận mua
5. Nhận email ngay lập tức

**💰 Thanh toán:**
• Hỗ trợ: Banking, Momo, Viettel Pay
• Tự động duyệt trong 1-5 phút
• Liên hệ admin nếu có vấn đề

**📞 Hỗ trợ:** Liên hệ admin qua bot"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /cancel"""
        # Xóa các trạng thái chờ input
        context.user_data.clear()
        
        user_id = update.effective_user.id
        is_admin = user_id in ADMIN_IDS
        
        welcome_message = MESSAGES["admin_welcome"] if is_admin else MESSAGES["user_welcome"]
        
        # Sử dụng persistent keyboard
        if is_admin:
            keyboard = get_persistent_keyboard_admin()
        else:
            keyboard = get_persistent_keyboard_user()
        
        await update.message.reply_text("❌ **Đã hủy thao tác!**\n\n" + welcome_message, reply_markup=keyboard, parse_mode='Markdown')
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý callback queries"""
        query = update.callback_query
        user_id = query.from_user.id
        data = query.data
        
        # Debug log
        logger.info(f"Received callback: {data} from user {user_id}")
        
        # Kiểm tra user bị ban
        if self.db.is_user_banned(user_id):
            await query.answer("🚫 Tài khoản của bạn đã bị khóa!", show_alert=True)
            return
        
        # Kiểm tra quyền admin
        is_admin = user_id in ADMIN_IDS
        
        try:
            # Admin callbacks
            if data.startswith('admin_') and is_admin:
                if data == 'admin_stats':
                    await admin_stats(update, context)
                elif data == 'admin_emails':
                    await query.edit_message_text("📧 **QUẢN LÝ EMAIL**", reply_markup=get_admin_emails_keyboard(), parse_mode='Markdown')
                elif data == 'admin_view_emails':
                    await admin_view_emails(update, context)
                elif data == 'admin_add_emails':
                    await admin_add_emails_prompt(update, context)
                elif data == 'admin_users':
                    await query.edit_message_text("👥 **QUẢN LÝ USER**", reply_markup=get_admin_users_keyboard(), parse_mode='Markdown')
                elif data == 'admin_list_users' or data.startswith('admin_list_users_'):
                    await admin_list_users(update, context)
                elif data == 'admin_ban_user':
                    await admin_ban_user_prompt(update, context)
                elif data == 'admin_add_balance':
                    await admin_add_balance_prompt(update, context)
                elif data == 'admin_view_orders':
                    await admin_view_orders(update, context)
                elif data == 'admin_settings':
                    await admin_settings(update, context)
                elif data == 'admin_deposits':
                    await admin_deposits(update, context)
                elif data == 'admin_back':
                    await admin_back(update, context)
                elif data == 'user_mode':
                    await query.edit_message_text(MESSAGES["user_welcome"], reply_markup=get_main_keyboard(is_admin=False), parse_mode='Markdown')
                # Settings callbacks
                elif data == 'admin_edit_price':
                    await admin_edit_price(update, context)
                elif data == 'admin_edit_payment':
                    await admin_edit_payment(update, context)
                elif data == 'admin_edit_product':
                    await admin_edit_product(update, context)
                elif data == 'admin_edit_bank_name':
                    await admin_edit_bank_name(update, context)
                elif data == 'admin_edit_account_number':
                    await admin_edit_account_number(update, context)
                elif data == 'admin_edit_account_name':
                    await admin_edit_account_name(update, context)
                # Contact info callbacks
                elif data == 'admin_edit_contact':
                    await admin_edit_contact(update, context)
                elif data == 'admin_edit_username':
                    await admin_edit_username(update, context)
                elif data == 'admin_edit_telegram_id':
                    await admin_edit_telegram_id(update, context)
                elif data == 'admin_edit_support_hours':
                    await admin_edit_support_hours(update, context)
                elif data == 'admin_edit_response_time':
                    await admin_edit_response_time(update, context)
                elif data == 'admin_edit_commitment':
                    await admin_edit_commitment(update, context)
                # Discount management callbacks
                elif data == 'admin_edit_discount':
                    await admin_edit_discount(update, context)
                elif data == 'admin_view_discount_rates':
                    await admin_view_discount_rates(update, context)
                elif data == 'admin_add_discount_rate':
                    await admin_add_discount_rate(update, context)
                elif data == 'admin_remove_discount_rate':
                    await admin_remove_discount_rate(update, context)
                elif data == 'admin_reset_discount_rates':
                    await admin_reset_discount_rates(update, context)
            
            # Deposit approval callbacks
            elif data.startswith('approve_deposit_') and is_admin:
                await approve_deposit(update, context)
            elif data.startswith('reject_deposit_') and is_admin:
                await reject_deposit(update, context)
            
            # User management callbacks
            elif data.startswith('ban_user_') and is_admin:
                await ban_user_action(update, context)
            elif data.startswith('unban_user_') and is_admin:
                await unban_user_action(update, context)
            elif data.startswith('add_balance_') and is_admin:
                await add_balance_action(update, context)
            
            # User callbacks
            elif data.startswith('user_'):
                if data == 'user_deposit':
                    await user_deposit(update, context)
                elif data == 'user_buy_email':
                    await user_buy_email(update, context)
                elif data == 'user_account':
                    await user_account(update, context)
                elif data == 'user_balance':
                    await user_balance(update, context)
                elif data == 'user_transactions':
                    await user_transactions(update, context)
                elif data == 'user_purchases':
                    await user_purchases(update, context)
                elif data == 'user_orders':
                    await user_orders(update, context)
                elif data == 'user_discount':
                    await user_discount(update, context)
                elif data == 'user_claim_discount':
                    await user_claim_discount(update, context)
                elif data == 'user_discount_rates':
                    await user_discount_rates(update, context)
                elif data == 'user_contact':
                    await user_contact(update, context)
                elif data == 'user_back':
                    await user_back(update, context)
            
            # Deposit callbacks
            elif data.startswith('deposit_'):
                if data.startswith('deposit_confirm_'):
                    await confirm_deposit(update, context)
                else:
                    await process_deposit_amount(update, context)
            
            # Purchase callbacks
            elif data.startswith('buy_email_'):
                await process_buy_email(update, context)
            elif data.startswith('confirm_purchase_'):
                await confirm_purchase(update, context)
            
            # Ignore callback
            elif data == 'ignore':
                await query.answer()
            
            else:
                await query.answer("❌ Lệnh không hợp lệ!")
                
        except Exception as e:
            logger.error(f"Lỗi xử lý callback {data}: {e}")
            await query.answer("❌ Có lỗi xảy ra! Vui lòng thử lại.")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý tin nhắn text"""
        user_id = update.effective_user.id
        
        # Kiểm tra user bị ban
        if self.db.is_user_banned(user_id):
            await update.message.reply_text("🚫 **Tài khoản của bạn đã bị khóa!**")
            return
        
        # Thêm user nếu chưa có
        user = update.effective_user
        self.db.add_user(user_id, user.username, user.first_name)
        
        # Xử lý input đặc biệt
        if context.user_data.get('waiting_for_emails') and user_id in ADMIN_IDS:
            await process_admin_add_emails(update, context)
        elif context.user_data.get('waiting_for_deposit_amount'):
            await process_custom_deposit_amount(update, context)
        elif context.user_data.get('waiting_for_email_quantity'):
            await process_custom_email_quantity(update, context)
        elif context.user_data.get('waiting_for_user_id') and user_id in ADMIN_IDS:
            await process_user_id_input(update, context)
        elif context.user_data.get('waiting_for_balance_amount') and user_id in ADMIN_IDS:
            await process_balance_amount_input(update, context)
        # Settings input handlers
        elif context.user_data.get('waiting_for_price') and user_id in ADMIN_IDS:
            await process_price_input(update, context)
        elif context.user_data.get('waiting_for_product_name') and user_id in ADMIN_IDS:
            await process_product_name_input(update, context)
        elif context.user_data.get('waiting_for_bank_name') and user_id in ADMIN_IDS:
            await process_bank_name_input(update, context)
        elif context.user_data.get('waiting_for_account_number') and user_id in ADMIN_IDS:
            await process_account_number_input(update, context)
        elif context.user_data.get('waiting_for_account_name') and user_id in ADMIN_IDS:
            await process_account_name_input(update, context)
        # Contact info input handlers
        elif context.user_data.get('waiting_for_username') and user_id in ADMIN_IDS:
            await process_username_input(update, context)
        elif context.user_data.get('waiting_for_telegram_id') and user_id in ADMIN_IDS:
            await process_telegram_id_input(update, context)
        elif context.user_data.get('waiting_for_support_hours') and user_id in ADMIN_IDS:
            await process_support_hours_input(update, context)
        elif context.user_data.get('waiting_for_response_time') and user_id in ADMIN_IDS:
            await process_response_time_input(update, context)
        elif context.user_data.get('waiting_for_commitment') and user_id in ADMIN_IDS:
            await process_commitment_input(update, context)
        # Discount management input handlers
        elif context.user_data.get('waiting_for_discount_quantity') and user_id in ADMIN_IDS:
            await process_discount_quantity_input(update, context)
        elif context.user_data.get('waiting_for_discount_amount') and user_id in ADMIN_IDS:
            await process_discount_amount_input(update, context)
        elif context.user_data.get('waiting_for_remove_discount_quantity') and user_id in ADMIN_IDS:
            await process_remove_discount_quantity_input(update, context)
        # Order ID input handler
        elif context.user_data.get('waiting_for_order_id'):
            await process_order_id_input(update, context)
        else:
            # Xử lý persistent keyboard buttons trước
            await self.handle_persistent_keyboard(update, context)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý lỗi"""
        logger.error(f"Lỗi: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ **Có lỗi xảy ra!**\n\nVui lòng thử lại sau hoặc liên hệ admin.", parse_mode='Markdown')
    
    async def setup_menu_button(self):
        """Thiết lập menu button dưới thanh chat"""
        try:
            # Tạo application để có thể gọi API
            if hasattr(self, 'application') and self.application:
                # Thiết lập menu button với commands
                menu_button = MenuButtonCommands()
                await self.application.bot.set_chat_menu_button(menu_button=menu_button)
                logger.info("Đã thiết lập menu button thành công")
        except Exception as e:
            logger.error(f"Lỗi thiết lập menu button: {e}")

    async def set_bot_commands(self):
        """Thiết lập danh sách commands cho bot"""
        from telegram import BotCommand
        
        commands = [
            BotCommand("start", "🚀 Khởi động bot"),
            BotCommand("help", "❓ Hướng dẫn sử dụng"),
            BotCommand("menu", "📋 Hiển thị menu chính"),
            BotCommand("balance", "💰 Kiểm tra số dư"),
            BotCommand("buy", "🛒 Mua email nhanh"),
            BotCommand("deposit", "💳 Nạp tiền"),
            BotCommand("contact", "📞 Liên hệ admin"),
            BotCommand("cancel", "❌ Hủy thao tác hiện tại")
        ]
        
        try:
            if hasattr(self, 'application') and self.application:
                await self.application.bot.set_my_commands(commands)
                logger.info("Đã thiết lập bot commands thành công")
        except Exception as e:
            logger.error(f"Lỗi thiết lập bot commands: {e}")

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /menu - Hiển thị menu chính"""
        user_id = update.effective_user.id
        
        # Kiểm tra user bị ban
        if self.db.is_user_banned(user_id):
            await update.message.reply_text("🚫 **Tài khoản của bạn đã bị khóa!**\n\n📞 Liên hệ admin để được hỗ trợ.", parse_mode='Markdown')
            return
        
        # Thêm user vào database
        user = update.effective_user
        self.db.add_user(user_id, user.username, user.first_name)
        
        # Kiểm tra admin
        is_admin = user_id in ADMIN_IDS
        
        welcome_message = MESSAGES["admin_welcome"] if is_admin else MESSAGES["user_welcome"]
        
        # Sử dụng persistent keyboard
        if is_admin:
            keyboard = get_persistent_keyboard_admin()
        else:
            keyboard = get_persistent_keyboard_user()
        
        await update.message.reply_text(welcome_message, reply_markup=keyboard, parse_mode='Markdown')

    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /balance - Kiểm tra số dư nhanh"""
        user_id = update.effective_user.id
        
        # Kiểm tra user bị ban
        if self.db.is_user_banned(user_id):
            await update.message.reply_text("🚫 **Tài khoản của bạn đã bị khóa!**", parse_mode='Markdown')
            return
        
        # Thêm user vào database
        user = update.effective_user
        self.db.add_user(user_id, user.username, user.first_name)
        
        balance = self.db.get_balance(user_id)
        product_price = settings_manager.get_product_price()
        
        text = f"""💰 **SỐ DƯ CỦA BẠN**

💳 **Số dư hiện tại:** {balance:,} VND

📊 **Thông tin:**
• 1 Email Gmail = {product_price:,} VND
• Có thể mua được: {balance // product_price} email

💡 **Lệnh nhanh:**
/buy - Mua email
/deposit - Nạp tiền
/menu - Menu chính"""
        
        await update.message.reply_text(text, parse_mode='Markdown')

    async def buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /buy - Mua email nhanh"""
        user_id = update.effective_user.id
        
        # Kiểm tra user bị ban
        if self.db.is_user_banned(user_id):
            await update.message.reply_text("🚫 **Tài khoản của bạn đã bị khóa!**", parse_mode='Markdown')
            return
        
        # Thêm user vào database
        user = update.effective_user
        self.db.add_user(user_id, user.username, user.first_name)
        
        # Kiểm tra số lượng email trong kho
        try:
            sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
            email_count = sheets.get_email_count()
        except:
            email_count = 0
        
        if email_count == 0:
            text = """❌ HẾT HÀNG

Hiện tại kho email đã hết hàng!
Vui lòng quay lại sau hoặc liên hệ admin.

📞 /contact - Liên hệ admin"""
            await update.message.reply_text(text)
            return
        
        text = f"""🛒 MUA EMAIL NHANH

💰 Giá: {settings_manager.get_product_price():,} VND/email
📦 Có sẵn: {email_count} email
✨ Chất lượng: Gmail mới, chưa sử dụng

Chọn số lượng email:"""
        
        keyboard = get_buy_email_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard)

    async def deposit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /deposit - Nạp tiền nhanh"""
        user_id = update.effective_user.id
        
        # Kiểm tra user bị ban
        if self.db.is_user_banned(user_id):
            await update.message.reply_text("🚫 **Tài khoản của bạn đã bị khóa!**", parse_mode='Markdown')
            return
        
        # Thêm user vào database
        user = update.effective_user
        self.db.add_user(user_id, user.username, user.first_name)
        
        text = """💳 **NẠP TIỀN NHANH**

Chọn số tiền bạn muốn nạp:

💰 Tỷ lệ: 1 VND = 1 VND
📱 Hỗ trợ: Banking, Momo, Viettel Pay"""
        
        keyboard = get_deposit_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')

    async def contact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /contact - Liên hệ admin"""
        # Lấy message liên hệ từ settings
        contact_text = settings_manager.get_contact_message()
        
        await update.message.reply_text(contact_text)

    async def handle_persistent_keyboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý các nút từ persistent keyboard"""
        text = update.message.text
        user_id = update.effective_user.id
        is_admin = user_id in ADMIN_IDS
        
        # Debug log
        logger.info(f"Processing persistent keyboard: '{text}' from user {user_id} (admin: {is_admin})")
        
        # Admin buttons
        if is_admin:
            if text == "📊 Thống kê":
                await self.show_admin_stats(update, context)
                return
            elif text == "📧 Quản lý Email":
                await self.show_email_management(update, context)
                return
            elif text == "👥 Quản lý User":
                await self.show_user_management(update, context)
                return
            elif text == "💰 Duyệt nạp tiền":
                await self.show_deposit_approval(update, context)
                return
            elif text == "⚙️ Cài đặt":
                await self.show_settings(update, context)
                return
            elif text == "👤 Chế độ User":
                await self.switch_to_user_mode(update, context)
                return
        
        # User buttons (cả admin và user đều có thể dùng)
        if text == "💳 Nạp tiền":
            await self.quick_deposit(update, context)
        elif text == "📧 Mua Email":
            await self.quick_buy_email(update, context)
        elif text == "👤 Tài khoản":
            await self.show_account_info(update, context)
        elif text == "💸 Chiết khấu":
            await self.show_discount_menu(update, context)
        elif text == "📞 Liên hệ":
            await self.show_contact_info(update, context)
        elif text == "📋 Menu":
            await self.show_inline_menu(update, context)
        else:
            # Nếu không khớp với nút nào, hiển thị menu mặc định
            logger.info(f"No button match for text: '{text}', showing default menu")
            welcome_message = MESSAGES["admin_welcome"] if is_admin else MESSAGES["user_welcome"]
            
            if is_admin:
                keyboard = get_persistent_keyboard_admin()
            else:
                keyboard = get_persistent_keyboard_user()
            
            await update.message.reply_text(
                "🤖 " + welcome_message, 
                reply_markup=keyboard, 
                parse_mode='Markdown'
            )

    # Admin button handlers
    async def show_admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị thống kê admin"""
        from admin_handlers import admin_stats
        # Tạo fake callback query để sử dụng admin_stats
        class FakeQuery:
            def __init__(self, user):
                self.from_user = user
                self.data = "admin_stats"
            async def answer(self): pass
            async def edit_message_text(self, *args, **kwargs):
                await update.message.reply_text(*args, **kwargs)
        
        fake_update = type('obj', (object,), {'callback_query': FakeQuery(update.effective_user)})()
        await admin_stats(fake_update, context)

    async def show_email_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị quản lý email"""
        text = "📧 **QUẢN LÝ EMAIL**"
        keyboard = get_admin_emails_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')

    async def show_user_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị quản lý user"""
        text = "👥 **QUẢN LÝ USER**"
        keyboard = get_admin_users_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')

    async def show_deposit_approval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị duyệt nạp tiền"""
        from admin_handlers import admin_deposits
        # Tạo fake callback query
        class FakeQuery:
            def __init__(self, user):
                self.from_user = user
                self.data = "admin_deposits"
            async def answer(self): pass
            async def edit_message_text(self, *args, **kwargs):
                await update.message.reply_text(*args, **kwargs)
        
        fake_update = type('obj', (object,), {'callback_query': FakeQuery(update.effective_user), 'effective_chat': update.effective_chat})()
        await admin_deposits(fake_update, context)

    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị cài đặt"""
        from admin_handlers import admin_settings
        # Tạo fake callback query
        class FakeQuery:
            def __init__(self, user):
                self.from_user = user
                self.data = "admin_settings"
            async def answer(self): pass
            async def edit_message_text(self, *args, **kwargs):
                await update.message.reply_text(*args, **kwargs)
        
        fake_update = type('obj', (object,), {'callback_query': FakeQuery(update.effective_user)})()
        await admin_settings(fake_update, context)

    async def switch_to_user_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Chuyển sang chế độ user"""
        keyboard = get_persistent_keyboard_user()
        await update.message.reply_text(
            "👤 **Đã chuyển sang chế độ User**\n\n" + MESSAGES["user_welcome"],
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    # User button handlers
    async def quick_deposit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Nạp tiền nhanh"""
        text = """💳 **NẠP TIỀN NHANH**

Chọn số tiền bạn muốn nạp:

💰 Tỷ lệ: 1 VND = 1 VND
📱 Hỗ trợ: Banking, Momo, Viettel Pay"""
        
        keyboard = get_deposit_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')

    async def quick_buy_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mua email nhanh"""
        # Kiểm tra số lượng email trong kho
        try:
            sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
            email_count = sheets.get_email_count()
        except:
            email_count = 0
        
        if email_count == 0:
            text = """❌ **HẾT HÀNG**

Hiện tại kho email đã hết hàng!
Vui lòng quay lại sau hoặc nhấn 📞 Liên hệ"""
            await update.message.reply_text(text, parse_mode='Markdown')
            return
        
        text = f"""🛒 MUA EMAIL NHANH

💰 Giá: {settings_manager.get_product_price():,} VND/email
📦 Có sẵn: {email_count} email
✨ Chất lượng: Gmail mới, chưa sử dụng

Chọn số lượng email:"""
        
        keyboard = get_buy_email_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard)

    async def show_account_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị thông tin tài khoản"""
        text = "👤 TÀI KHOẢN CỦA BẠN\n\nChọn thông tin bạn muốn xem:"
        keyboard = get_user_account_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard)

    async def show_contact_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị thông tin liên hệ"""
        # Lấy message liên hệ từ settings
        contact_text = settings_manager.get_contact_message()
        
        await update.message.reply_text(contact_text)

    async def quick_balance_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kiểm tra số dư nhanh"""
        user_id = update.effective_user.id
        balance = self.db.get_balance(user_id)
        product_price = settings_manager.get_product_price()
        
        text = f"""💰 SỐ DƯ NHANH

💳 Số dư: {balance:,} VND
🛒 Có thể mua: {balance // product_price} email

💡 Nhấn "📧 Mua Email" để mua ngay!"""
        
        await update.message.reply_text(text)

    async def show_inline_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị menu inline đầy đủ"""
        user_id = update.effective_user.id
        is_admin = user_id in ADMIN_IDS
        
        welcome_message = MESSAGES["admin_welcome"] if is_admin else MESSAGES["user_welcome"]
        keyboard = get_main_keyboard(is_admin=is_admin)
        
        await update.message.reply_text(welcome_message, reply_markup=keyboard, parse_mode='Markdown')

    async def show_discount_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị menu chiết khấu"""
        from user_handlers import user_discount
        # Tạo fake callback query
        class FakeQuery:
            def __init__(self, user):
                self.from_user = user
                self.data = "user_discount"
            async def answer(self): pass
            async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
                await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        
        fake_update = Update(update.update_id, message=update.message, callback_query=FakeQuery(update.effective_user))
        await user_discount(fake_update, context)

    def run(self):
        """Chạy bot"""
        if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            logger.error("Vui lòng cấu hình BOT_TOKEN trong config.py!")
            return
        
        # Tạo application
        application = Application.builder().token(BOT_TOKEN).build()
        self.application = application  # Lưu application để sử dụng sau này
        
        # Thêm handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("cancel", self.cancel_command))
        application.add_handler(CommandHandler("menu", self.menu_command))
        application.add_handler(CommandHandler("balance", self.balance_command))
        application.add_handler(CommandHandler("buy", self.buy_command))
        application.add_handler(CommandHandler("deposit", self.deposit_command))
        application.add_handler(CommandHandler("contact", self.contact_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        # Error handler
        application.add_error_handler(self.error_handler)
        
        # Setup menu button và commands khi khởi động
        async def post_init(app):
            await self.set_bot_commands()
            await self.setup_menu_button()
        
        application.post_init = post_init
        
        logger.info("🤖 Bot đang khởi động...")
        logger.info(f"📊 Admin IDs: {ADMIN_IDS}")
        
        # Chạy bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = GmailBot()
    bot.run()
