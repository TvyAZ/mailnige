from telegram import Update
from telegram.ext import ContextTypes
import logging
from database import Database
from google_sheets import GoogleSheetsManager
from keyboards import *
from config import *
from settings_manager import settings_manager
import math
import datetime

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị thống kê hệ thống"""
    query = update.callback_query
    await query.answer()
    
    db = Database(DATABASE_FILE)
    stats = db.get_stats()
    
    # Lấy số lượng email trong kho
    try:
        sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
        email_count = sheets.get_email_count()
    except:
        email_count = "N/A"
    
    stats_text = f"""📊 **THỐNG KÊ HỆ THỐNG**

👥 **Người dùng:**
   • Tổng số user: {stats['total_users']:,}
   • User mới hôm nay: {stats['new_users_today']:,}

💰 **Doanh thu:**
   • Tổng doanh thu: {stats['total_revenue']:,} VND
   • Doanh thu hôm nay: {stats['revenue_today']:,} VND
   • Tổng tiền nạp: {stats['total_deposits']:,} VND

📧 **Kho email:**
   • Số lượng email: {email_count}

📅 **Cập nhật:** {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"""
    
    await query.edit_message_text(stats_text, reply_markup=get_back_keyboard("admin_back"), parse_mode='Markdown')

async def admin_view_emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem kho email"""
    query = update.callback_query
    await query.answer()
    
    try:
        sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
        email_count = sheets.get_email_count()
        emails_preview = sheets.get_all_emails_preview(10)
        
        text = f"📧 **KHO EMAIL**\n\n"
        text += f"📊 Tổng số email: **{email_count}**\n\n"
        
        if emails_preview:
            text += "📋 **10 email đầu tiên:**\n"
            for i, (email, password) in enumerate(emails_preview, 1):
                text += f"`{i}.` {email[:20]}{'...' if len(email) > 20 else ''}:{password[:10]}{'...' if len(password) > 10 else ''}\n"
        else:
            text += "❌ Kho email trống!"
        
    except Exception as e:
        text = f"❌ Lỗi kết nối Google Sheets: {str(e)}"
    
    await query.edit_message_text(text, reply_markup=get_admin_emails_keyboard(), parse_mode='Markdown')

async def admin_add_emails_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt thêm email"""
    query = update.callback_query
    await query.answer()
    
    text = """➕ **THÊM EMAIL**

Gửi danh sách email theo định dạng:
```
email1@gmail.com:password1
email2@gmail.com:password2
email3@gmail.com:password3
```

📝 **Lưu ý:**
• Mỗi dòng một email:password
• Tối đa 100 email/lần
• Dùng /cancel để hủy

Vui lòng gửi danh sách email:"""
    
    context.user_data['waiting_for_emails'] = True
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_emails"), parse_mode='Markdown')

async def process_admin_add_emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý thêm email từ admin với batch processing"""
    if not context.user_data.get('waiting_for_emails'):
        return
    
    context.user_data['waiting_for_emails'] = False
    
    text = update.message.text
    emails = [line.strip() for line in text.split('\n') if line.strip() and ':' in line]
    
    if not emails:
        await update.message.reply_text("❌ Không tìm thấy email hợp lệ! Định dạng: email:password")
        return
    
    if len(emails) > 100:
        await update.message.reply_text("❌ Tối đa 100 email/lần!")
        return
    
    # Thông báo bắt đầu xử lý
    processing_msg = await update.message.reply_text(f"⏳ Đang thêm {len(emails)} email vào kho...\n💡 Vui lòng chờ để tránh rate limit!")
    
    try:
        sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
        
        # Kiểm tra rate limit trước khi thêm
        operations_needed = (len(emails) + 2) // 3  # Số batch cần thiết
        if not sheets.is_rate_limit_safe(operations_needed):
            await processing_msg.edit_text(
                f"⚠️ **Rate limit warning!**\n\n"
                f"Cần {operations_needed} operations để thêm {len(emails)} email.\n"
                f"Hiện tại đã sử dụng nhiều quota, vui lòng chờ 1-2 phút rồi thử lại.\n\n"
                f"💡 Hoặc giảm số lượng email xuống ≤9 email để thêm ngay.",
                reply_markup=get_admin_emails_keyboard(),
                parse_mode='Markdown'
            )
            return
        
        # Sử dụng batch processing để tránh rate limit
        added_count = sheets.add_emails_batch(emails, batch_size=3)  # Giảm batch size xuống 3
        
        if added_count > 0:
            success_text = f"✅ **Đã thêm thành công {added_count}/{len(emails)} email vào kho!**"
            if added_count < len(emails):
                success_text += f"\n⚠️ {len(emails) - added_count} email bị lỗi do rate limit, vui lòng thử lại sau."
        else:
            success_text = "❌ Không thể thêm email. Có thể do rate limit hoặc lỗi kết nối!"
            
        # Cập nhật message
        await processing_msg.edit_text(success_text, reply_markup=get_admin_emails_keyboard(), parse_mode='Markdown')
            
    except Exception as e:
        error_msg = str(e)
        
        if "quota exceeded" in error_msg.lower() or "rate_limit" in error_msg.lower() or "429" in error_msg:
            error_text = f"""⚠️ **RATE LIMIT EXCEEDED!**

🚫 **Lỗi:** Google Sheets API đã vượt quá giới hạn
📊 **Giới hạn:** 60 write requests/phút
⏱️ **Khuyến nghị:** Chờ 2-5 phút rồi thử lại

💡 **Cách khắc phục:**
1. ⏳ Chờ 2-5 phút để quota reset
2. 📉 Giảm số lượng email xuống ≤9 email/lần
3. 🔄 Kiểm tra trạng thái Google Sheets
4. 📱 Thử lại với batch nhỏ hơn

🛡️ **Lưu ý:** Hệ thống đã được tối ưu để tránh rate limit, nhưng do lượng thao tác lớn nên vẫn có thể gặp lỗi này."""
        else:
            error_text = f"""❌ **LỖI THÊM EMAIL**

⚠️ **Chi tiết:** {error_msg}

💡 **Cách khắc phục:**
• Kiểm tra kết nối Google Sheets
• Đảm bảo định dạng email:password đúng
• Thử lại sau vài phút"""
        
        await processing_msg.edit_text(error_text, reply_markup=get_admin_emails_keyboard(), parse_mode='Markdown')

async def admin_deposits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem danh sách nạp tiền chờ duyệt"""
    query = update.callback_query
    await query.answer()
    
    db = Database(DATABASE_FILE)
    pending_deposits = db.get_pending_deposits()
    
    if not pending_deposits:
        text = "💰 **DUYỆT NẠP TIỀN**\n\n✅ Không có giao dịch nào chờ duyệt!"
        await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_back"), parse_mode='Markdown')
        return
    
    text = "💰 **DANH SÁCH NẠP TIỀN CHỜ DUYỆT**\n\n"
    
    for deposit in pending_deposits[:10]:  # Hiển thị tối đa 10
        trans_id, user_id, username, first_name, amount, created_at = deposit
        user_name = username or first_name or f"User {user_id}"
        text += f"🔸 **ID:** {trans_id}\n"
        text += f"👤 **User:** {user_name} (`{user_id}`)\n"
        text += f"💰 **Số tiền:** {amount:,} VND\n"
        text += f"📅 **Thời gian:** {created_at}\n"
        
        # Tạo keyboard cho từng giao dịch
        keyboard = get_admin_deposit_approval_keyboard(trans_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"💳 **Nạp tiền #{trans_id}**\n\n"
                 f"👤 User: {user_name}\n"
                 f"💰 Số tiền: {amount:,} VND\n"
                 f"📅 {created_at}",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    await query.edit_message_text("💰 **DUYỆT NẠP TIỀN**\n\nDanh sách giao dịch chờ duyệt:", reply_markup=get_back_keyboard("admin_back"), parse_mode='Markdown')

async def approve_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyệt nạp tiền"""
    query = update.callback_query
    await query.answer()
    
    transaction_id = int(query.data.split('_')[2])
    
    db = Database(DATABASE_FILE)
    success = db.approve_deposit(transaction_id)
    
    if success:
        # Lấy thông tin giao dịch để thông báo user
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, amount FROM transactions WHERE id = ?', (transaction_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, amount = result
            
            # Thông báo cho user
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"✅ **NẠP TIỀN THÀNH CÔNG**\n\n"
                         f"💰 Số tiền: {amount:,} VND\n"
                         f"✨ Giao dịch đã được duyệt!",
                    parse_mode='Markdown'
                )
            except:
                pass
        
        await query.edit_message_text("✅ **Đã duyệt nạp tiền thành công!**", parse_mode='Markdown')
    else:
        await query.edit_message_text("❌ **Lỗi duyệt nạp tiền!**", parse_mode='Markdown')

async def reject_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Từ chối nạp tiền"""
    query = update.callback_query
    await query.answer()
    
    transaction_id = int(query.data.split('_')[2])
    
    db = Database(DATABASE_FILE)
    
    # Lấy thông tin giao dịch trước khi từ chối
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, amount FROM transactions WHERE id = ?', (transaction_id,))
    result = cursor.fetchone()
    conn.close()
    
    db.reject_deposit(transaction_id)
    
    if result:
        user_id, amount = result
        
        # Thông báo cho user
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"❌ **NẠP TIỀN BỊ TỪ CHỐI**\n\n"
                     f"💰 Số tiền: {amount:,} VND\n"
                     f"📞 Liên hệ admin để được hỗ trợ.",
                parse_mode='Markdown'
            )
        except:
            pass
    
    await query.edit_message_text("❌ **Đã từ chối nạp tiền!**", parse_mode='Markdown')

async def admin_list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Danh sách user với phân trang"""
    query = update.callback_query
    await query.answer()
    
    # Lấy trang hiện tại
    if query.data == 'admin_list_users':
        page = 1
    elif query.data.startswith('admin_list_users_'):
        try:
            page = int(query.data.split('_')[-1])
        except ValueError:
            page = 1
    else:
        page = 1
    
    db = Database(DATABASE_FILE)
    all_users = db.get_all_users()
    
    users_per_page = 10
    total_pages = math.ceil(len(all_users) / users_per_page)
    start_idx = (page - 1) * users_per_page
    end_idx = start_idx + users_per_page
    current_users = all_users[start_idx:end_idx]
    
    text = f"👥 **DANH SÁCH USER** (Trang {page}/{total_pages})\n\n"
    
    for user in current_users:
        user_id, username, first_name, balance, created_at, is_banned = user
        user_name = username or first_name or f"User {user_id}"
        status = "🚫" if is_banned else "✅"
        
        text += f"{status} **{user_name}** (`{user_id}`)\n"
        text += f"💰 {balance:,} VND | 📅 {created_at[:10]}\n\n"
    
    keyboard = get_pagination_keyboard(page, total_pages, "admin_list_users")
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quay lại menu admin"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        MESSAGES["admin_welcome"],
        reply_markup=get_main_keyboard(is_admin=True)
    )

async def admin_ban_user_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt ban/unban user"""
    query = update.callback_query
    await query.answer()
    
    text = """🚫 **BAN/UNBAN USER**

Nhập Telegram ID của user bạn muốn ban/unban:

📝 **Lưu ý:**
• Nhập đúng Telegram ID (số)
• Dùng /cancel để hủy

Nhập User ID:"""
    
    context.user_data['waiting_for_user_id'] = 'ban'
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_users"), parse_mode='Markdown')

async def admin_add_balance_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt cộng tiền user"""
    query = update.callback_query
    await query.answer()
    
    text = """💰 **CỘNG TIỀN USER**

Nhập Telegram ID của user bạn muốn cộng tiền:

📝 **Lưu ý:**
• Nhập đúng Telegram ID (số)
• Dùng /cancel để hủy

Nhập User ID:"""
    
    context.user_data['waiting_for_user_id'] = 'balance'
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_users"), parse_mode='Markdown')

async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cài đặt hệ thống"""
    query = update.callback_query
    await query.answer()
    
    # Lấy thông tin cài đặt hiện tại
    try:
        sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
        email_count = sheets.get_email_count()
        sheets_status = "✅ Kết nối"
    except:
        email_count = "N/A"
        sheets_status = "❌ Lỗi kết nối"
    
    # Lấy cài đặt từ settings manager
    product_price = settings_manager.get_product_price()
    product_name = settings_manager.get_product_name()
    payment_info = settings_manager.get_payment_info()
    
    text = f"""⚙️ CÀI ĐẶT HỆ THỐNG

📧 Sản phẩm:
• Tên: {product_name}
• Giá: {product_price:,} VND/email
• Kho: {email_count} email
• Google Sheets: {sheets_status}

🏦 Thanh toán:
• Bank: {payment_info['bank_name']}
• STK: {payment_info['account_number']}
• Tên: {payment_info['account_name']}

👑 Admin:
• Admin IDs: {', '.join(map(str, ADMIN_IDS))}
• Database: {DATABASE_FILE}

💡 Nhấn các nút bên dưới để chỉnh sửa cài đặt"""
    
    await query.edit_message_text(text, reply_markup=get_admin_settings_keyboard())

# ==================== SETTINGS MANAGEMENT ====================

async def admin_edit_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chỉnh sửa giá sản phẩm"""
    query = update.callback_query
    await query.answer()
    
    current_price = settings_manager.get_product_price()
    
    text = f"""💰 CHỈNH SỬA GIÁ SẢN PHẨM

Giá hiện tại: {current_price:,} VND/email

📝 Vui lòng nhập giá mới (chỉ số, ví dụ: 5000):"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_settings"))
    
    # Đặt trạng thái chờ input
    context.user_data['waiting_for_price'] = True

async def admin_edit_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu chỉnh sửa thông tin thanh toán"""
    query = update.callback_query
    await query.answer()
    
    payment_info = settings_manager.get_payment_info()
    
    text = f"""🏦 THÔNG TIN THANH TOÁN HIỆN TẠI

• Bank: {payment_info['bank_name']}
• STK: {payment_info['account_number']}
• Tên: {payment_info['account_name']}

Chọn thông tin muốn chỉnh sửa:"""
    
    await query.edit_message_text(text, reply_markup=get_admin_payment_keyboard())

async def admin_edit_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chỉnh sửa thông tin sản phẩm"""
    query = update.callback_query
    await query.answer()
    
    product_name = settings_manager.get_product_name()
    
    text = f"""📧 CHỈNH SỬA TÊN SẢN PHẨM

Tên hiện tại: {product_name}

📝 Vui lòng nhập tên sản phẩm mới:"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_settings"))
    
    # Đặt trạng thái chờ input
    context.user_data['waiting_for_product_name'] = True

async def admin_edit_bank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chỉnh sửa tên ngân hàng"""
    query = update.callback_query
    await query.answer()
    
    payment_info = settings_manager.get_payment_info()
    
    text = f"""🏦 CHỈNH SỬA TÊN NGÂN HÀNG

Tên hiện tại: {payment_info['bank_name']}

📝 Vui lòng nhập tên ngân hàng mới:"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_edit_payment"))
    
    # Đặt trạng thái chờ input
    context.user_data['waiting_for_bank_name'] = True

async def admin_edit_account_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chỉnh sửa số tài khoản"""
    query = update.callback_query
    await query.answer()
    
    payment_info = settings_manager.get_payment_info()
    
    text = f"""💳 CHỈNH SỬA SỐ TÀI KHOẢN

STK hiện tại: {payment_info['account_number']}

📝 Vui lòng nhập số tài khoản mới:"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_edit_payment"))
    
    # Đặt trạng thái chờ input
    context.user_data['waiting_for_account_number'] = True

async def admin_edit_account_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chỉnh sửa tên chủ tài khoản"""
    query = update.callback_query
    await query.answer()
    
    payment_info = settings_manager.get_payment_info()
    
    text = f"""👤 CHỈNH SỬA TÊN CHỦ TÀI KHOẢN

Tên hiện tại: {payment_info['account_name']}

📝 Vui lòng nhập tên chủ tài khoản mới:"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_edit_payment"))
    
    # Đặt trạng thái chờ input
    context.user_data['waiting_for_account_name'] = True

async def admin_edit_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu chỉnh sửa thông tin liên hệ"""
    query = update.callback_query
    await query.answer()
    
    contact_info = settings_manager.get_contact_info()
    
    text = f"""📞 THÔNG TIN LIÊN HỆ HIỆN TẠI

👤 Admin: {contact_info['admin_username']}
📱 Telegram ID: {contact_info['admin_telegram_id']}
🕒 Hỗ trợ: {contact_info['support_hours']}
⚡ Phản hồi: {contact_info['response_time']}
🛡️ Cam kết: {contact_info['commitment']}

Chọn thông tin muốn chỉnh sửa:"""
    
    await query.edit_message_text(text, reply_markup=get_admin_contact_keyboard())

async def process_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input giá sản phẩm"""
    try:
        new_price = int(update.message.text.replace(',', '').replace('.', '').strip())
        
        if new_price <= 0:
            await update.message.reply_text("❌ Giá phải lớn hơn 0!")
            return
        
        if settings_manager.set_product_price(new_price):
            await update.message.reply_text(f"✅ Đã cập nhật giá sản phẩm: {new_price:,} VND/email")
        else:
            await update.message.reply_text("❌ Lỗi khi lưu cài đặt!")
            
    except ValueError:
        await update.message.reply_text("❌ Vui lòng nhập số hợp lệ!")
    
    # Xóa trạng thái chờ
    context.user_data.pop('waiting_for_price', None)

async def process_product_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input tên sản phẩm"""
    new_name = update.message.text.strip()
    
    if len(new_name) < 2:
        await update.message.reply_text("❌ Tên sản phẩm phải có ít nhất 2 ký tự!")
        return
    
    if settings_manager.set_product_name(new_name):
        await update.message.reply_text(f"✅ Đã cập nhật tên sản phẩm: {new_name}")
    else:
        await update.message.reply_text("❌ Lỗi khi lưu cài đặt!")
    
    # Xóa trạng thái chờ
    context.user_data.pop('waiting_for_product_name', None)

async def process_bank_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input tên ngân hàng"""
    new_bank_name = update.message.text.strip()
    
    if len(new_bank_name) < 3:
        await update.message.reply_text("❌ Tên ngân hàng phải có ít nhất 3 ký tự!")
        return
    
    if settings_manager.set_bank_name(new_bank_name):
        await update.message.reply_text(f"✅ Đã cập nhật tên ngân hàng: {new_bank_name}")
    else:
        await update.message.reply_text("❌ Lỗi khi lưu cài đặt!")
    
    # Xóa trạng thái chờ
    context.user_data.pop('waiting_for_bank_name', None)

async def process_account_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input số tài khoản"""
    new_account_number = update.message.text.strip()
    
    if len(new_account_number) < 6:
        await update.message.reply_text("❌ Số tài khoản phải có ít nhất 6 ký tự!")
        return
    
    if settings_manager.set_account_number(new_account_number):
        await update.message.reply_text(f"✅ Đã cập nhật số tài khoản: {new_account_number}")
    else:
        await update.message.reply_text("❌ Lỗi khi lưu cài đặt!")
    
    # Xóa trạng thái chờ
    context.user_data.pop('waiting_for_account_number', None)

async def process_account_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input tên chủ tài khoản"""
    new_account_name = update.message.text.strip().upper()
    
    if len(new_account_name) < 3:
        await update.message.reply_text("❌ Tên chủ tài khoản phải có ít nhất 3 ký tự!")
        return
    
    if settings_manager.set_account_name(new_account_name):
        await update.message.reply_text(f"✅ Đã cập nhật tên chủ tài khoản: {new_account_name}")
    else:
        await update.message.reply_text("❌ Lỗi khi lưu cài đặt!")
    
    # Xóa trạng thái chờ
    context.user_data.pop('waiting_for_account_name', None)

async def admin_edit_price_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý chỉnh sửa giá sản phẩm từ inline button"""
    query = update.callback_query
    await query.answer()
    
    transaction_id = int(query.data.split('_')[2])
    
    db = Database(DATABASE_FILE)
    deposit = db.get_deposit(transaction_id)
    
    if not deposit:
        await query.edit_message_text("❌ Không tìm thấy giao dịch nạp tiền này!")
        return
    
    user_id, amount = deposit[1], deposit[4]
    
    # Thông báo cho user về giao dịch nạp tiền
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"💳 **YÊU CẦU NẠP TIỀN**\n\n"
                 f"🆔 **ID giao dịch:** {transaction_id}\n"
                 f"💰 **Số tiền:** {amount:,} VND\n"
                 f"📅 **Thời gian:** {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                 "Vui lòng xác nhận để hoàn tất nạp tiền.",
            parse_mode='Markdown'
        )
    except:
        pass
    
    await query.edit_message_text("✅ Đã gửi yêu cầu nạp tiền đến user!", parse_mode='Markdown')

async def admin_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem giá sản phẩm hiện tại"""
    query = update.callback_query
    await query.answer()
    
    current_price = settings_manager.get_product_price()
    
    text = f"💰 **GIÁ SẢN PHẨM HIỆN TẠI**\n\n• {current_price:,} VND/email"
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_settings"), parse_mode='Markdown')

async def admin_payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem thông tin thanh toán hiện tại"""
    query = update.callback_query
    await query.answer()
    
    payment_info = settings_manager.get_payment_info()
    
    text = f"""🏦 **THÔNG TIN THANH TOÁN HIỆN TẠI**

• **Ngân hàng:** {payment_info['bank_name']}
• **Số tài khoản:** {payment_info['account_number']}
• **Tên chủ tài khoản:** {payment_info['account_name']}"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_settings"), parse_mode='Markdown')

async def admin_edit_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem và chỉnh sửa tên sản phẩm"""
    query = update.callback_query
    await query.answer()
    
    product_name = settings_manager.get_product_name()
    
    text = f"""📧 **TÊN SẢN PHẨM HIỆN TẠI**

Tên: {product_name}

📝 Vui lòng nhập tên sản phẩm mới:"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_settings"), parse_mode='Markdown')

async def admin_edit_bank_name_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý chỉnh sửa tên ngân hàng từ inline button"""
    query = update.callback_query
    await query.answer()
    
    transaction_id = int(query.data.split('_')[2])
    
    db = Database(DATABASE_FILE)
    deposit = db.get_deposit(transaction_id)
    
    if not deposit:
        await query.edit_message_text("❌ Không tìm thấy giao dịch nạp tiền này!")
        return
    
    user_id, amount = deposit[1], deposit[4]
    
    # Thông báo cho user về giao dịch nạp tiền
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"💳 **YÊU CẦU NẠP TIỀN**\n\n"
                 f"🆔 **ID giao dịch:** {transaction_id}\n"
                 f"💰 **Số tiền:** {amount:,} VND\n"
                 f"📅 **Thời gian:** {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                 "Vui lòng xác nhận để hoàn tất nạp tiền.",
            parse_mode='Markdown'
        )
    except:
        pass
    
    await query.edit_message_text("✅ Đã gửi yêu cầu nạp tiền đến user!", parse_mode='Markdown')

async def admin_edit_account_number_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý chỉnh sửa số tài khoản từ inline button"""
    query = update.callback_query
    await query.answer()
    
    transaction_id = int(query.data.split('_')[2])
    
    db = Database(DATABASE_FILE)
    deposit = db.get_deposit(transaction_id)
    
    if not deposit:
        await query.edit_message_text("❌ Không tìm thấy giao dịch nạp tiền này!")
        return
    
    user_id, amount = deposit[1], deposit[4]
    
    # Thông báo cho user về giao dịch nạp tiền
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"💳 **YÊU CẦU NẠP TIỀN**\n\n"
                 f"🆔 **ID giao dịch:** {transaction_id}\n"
                 f"💰 **Số tiền:** {amount:,} VND\n"
                 f"📅 **Thời gian:** {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                 "Vui lòng xác nhận để hoàn tất nạp tiền.",
            parse_mode='Markdown'
        )
    except:
        pass
    
    await query.edit_message_text("✅ Đã gửi yêu cầu nạp tiền đến user!", parse_mode='Markdown')

async def admin_edit_account_name_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý chỉnh sửa tên chủ tài khoản từ inline button"""
    query = update.callback_query
    await query.answer()
    
    transaction_id = int(query.data.split('_')[2])
    
    db = Database(DATABASE_FILE)
    deposit = db.get_deposit(transaction_id)
    
    if not deposit:
        await query.edit_message_text("❌ Không tìm thấy giao dịch nạp tiền này!")
        return
    
    user_id, amount = deposit[1], deposit[4]
    
    # Thông báo cho user về giao dịch nạp tiền
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"💳 **YÊU CẦU NẠP TIỀN**\n\n"
                 f"🆔 **ID giao dịch:** {transaction_id}\n"
                 f"💰 **Số tiền:** {amount:,} VND\n"
                 f"📅 **Thời gian:** {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                 "Vui lòng xác nhận để hoàn tất nạp tiền.",
            parse_mode='Markdown'
        )
    except:
        pass
    
    await query.edit_message_text("✅ Đã gửi yêu cầu nạp tiền đến user!", parse_mode='Markdown')

# ==================== CONTACT INFO EDIT HANDLERS ====================

async def admin_edit_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chỉnh sửa username admin"""
    query = update.callback_query
    await query.answer()
    
    contact_info = settings_manager.get_contact_info()
    
    text = f"""👤 CHỈNH SỬA USERNAME ADMIN

Username hiện tại: {contact_info['admin_username']}

Nhập username mới (có thể có hoặc không có @):
Ví dụ: @admin_support hoặc admin_support"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_edit_contact"))
    
    # Đặt trạng thái chờ input
    context.user_data['waiting_for_username'] = True

async def admin_edit_telegram_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chỉnh sửa Telegram ID admin"""
    query = update.callback_query
    await query.answer()
    
    contact_info = settings_manager.get_contact_info()
    
    text = f"""📱 CHỈNH SỬA TELEGRAM ID

Telegram ID hiện tại: {contact_info['admin_telegram_id']}

Nhập Telegram ID mới:
Ví dụ: 890641298"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_edit_contact"))
    
    # Đặt trạng thái chờ input
    context.user_data['waiting_for_telegram_id'] = True

async def admin_edit_support_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chỉnh sửa giờ hỗ trợ"""
    query = update.callback_query
    await query.answer()
    
    contact_info = settings_manager.get_contact_info()
    
    text = f"""🕒 CHỈNH SỬA GIỜ HỖ TRỢ

Giờ hỗ trợ hiện tại: {contact_info['support_hours']}

Nhập giờ hỗ trợ mới:
Ví dụ: 24/7, 8:00-22:00, Thứ 2-7: 9h-18h"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_edit_contact"))
    
    # Đặt trạng thái chờ input
    context.user_data['waiting_for_support_hours'] = True

async def admin_edit_response_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chỉnh sửa thời gian phản hồi"""
    query = update.callback_query
    await query.answer()
    
    contact_info = settings_manager.get_contact_info()
    
    text = f"""⚡ CHỈNH SỬA THỜI GIAN PHẢN HỒI

Thời gian phản hồi hiện tại: {contact_info['response_time']}

Nhập thời gian phản hồi mới:
Ví dụ: Phản hồi nhanh trong 5 phút!, Phản hồi trong 1-3 phút"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_edit_contact"))
    
    # Đặt trạng thái chờ input
    context.user_data['waiting_for_response_time'] = True

async def admin_edit_commitment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chỉnh sửa cam kết hỗ trợ"""
    query = update.callback_query
    await query.answer()
    
    contact_info = settings_manager.get_contact_info()
    
    text = f"""🛡️ CHỈNH SỬA CAM KẾT HỖ TRỢ

Cam kết hiện tại: {contact_info['commitment']}

Nhập cam kết hỗ trợ mới:
Ví dụ: Cam kết hỗ trợ tận tình!, Dịch vụ chất lượng cao"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_edit_contact"))
    
    # Đặt trạng thái chờ input
    context.user_data['waiting_for_commitment'] = True

# ==================== CONTACT INFO INPUT PROCESSORS ====================

async def process_username_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input username admin"""
    new_username = update.message.text.strip()
    
    if len(new_username) < 2:
        await update.message.reply_text("❌ Username quá ngắn! Vui lòng nhập lại.")
        return
    
    if settings_manager.set_admin_username(new_username):
        await update.message.reply_text(f"✅ Đã cập nhật username admin: {new_username}")
    else:
        await update.message.reply_text("❌ Lỗi cập nhật username! Vui lòng thử lại.")
    
    # Xóa trạng thái chờ input
    context.user_data.pop('waiting_for_username', None)

async def process_telegram_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input Telegram ID"""
    new_telegram_id = update.message.text.strip()
    
    if not new_telegram_id.isdigit():
        await update.message.reply_text("❌ Telegram ID phải là số! Vui lòng nhập lại.")
        return
    
    if settings_manager.set_admin_telegram_id(new_telegram_id):
        await update.message.reply_text(f"✅ Đã cập nhật Telegram ID: {new_telegram_id}")
    else:
        await update.message.reply_text("❌ Lỗi cập nhật Telegram ID! Vui lòng thử lại.")
    
    # Xóa trạng thái chờ input
    context.user_data.pop('waiting_for_telegram_id', None)

async def process_support_hours_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input giờ hỗ trợ"""
    new_hours = update.message.text.strip()
    
    if len(new_hours) < 2:
        await update.message.reply_text("❌ Giờ hỗ trợ quá ngắn! Vui lòng nhập lại.")
        return
    
    if settings_manager.set_support_hours(new_hours):
        await update.message.reply_text(f"✅ Đã cập nhật giờ hỗ trợ: {new_hours}")
    else:
        await update.message.reply_text("❌ Lỗi cập nhật giờ hỗ trợ! Vui lòng thử lại.")
    
    # Xóa trạng thái chờ input
    context.user_data.pop('waiting_for_support_hours', None)

async def process_response_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input thời gian phản hồi"""
    new_response_time = update.message.text.strip()
    
    if len(new_response_time) < 3:
        await update.message.reply_text("❌ Thời gian phản hồi quá ngắn! Vui lòng nhập lại.")
        return
    
    if settings_manager.set_response_time(new_response_time):
        await update.message.reply_text(f"✅ Đã cập nhật thời gian phản hồi: {new_response_time}")
    else:
        await update.message.reply_text("❌ Lỗi cập nhật thời gian phản hồi! Vui lòng thử lại.")
    
    # Xóa trạng thái chờ input
    context.user_data.pop('waiting_for_response_time', None)

async def process_commitment_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input cam kết hỗ trợ"""
    new_commitment = update.message.text.strip()
    
    if len(new_commitment) < 3:
        await update.message.reply_text("❌ Cam kết hỗ trợ quá ngắn! Vui lòng nhập lại.")
        return
    
    if settings_manager.set_commitment(new_commitment):
        await update.message.reply_text(f"✅ Đã cập nhật cam kết hỗ trợ: {new_commitment}")
    else:
        await update.message.reply_text("❌ Lỗi cập nhật cam kết hỗ trợ! Vui lòng thử lại.")
    
    # Xóa trạng thái chờ input
    context.user_data.pop('waiting_for_commitment', None)

# ==================== USER MANAGEMENT INPUT PROCESSORS ====================

async def process_user_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input User ID cho ban/unban hoặc cộng tiền"""
    user_id_input = update.message.text.strip()
    
    # Kiểm tra User ID hợp lệ
    if not user_id_input.isdigit():
        await update.message.reply_text("❌ User ID phải là số! Vui lòng nhập lại.")
        return
    
    target_user_id = int(user_id_input)
    action = context.user_data.get('waiting_for_user_id')
    
    if action == 'ban':
        # Xử lý ban/unban user
        await handle_ban_unban_user(update, context, target_user_id)
    elif action == 'balance':
        # Chuyển sang bước nhập số tiền
        context.user_data['target_user_id'] = target_user_id
        context.user_data['waiting_for_balance_amount'] = True
        context.user_data.pop('waiting_for_user_id', None)
        
        # Kiểm tra user có tồn tại không
        db = Database(DATABASE_FILE)
        user_info = db.get_user_info(target_user_id)
        
        if user_info:
            username, first_name = user_info[1], user_info[2]
            display_name = f"@{username}" if username else first_name or f"ID:{target_user_id}"
            
            text = f"""💰 CỘNG TIỀN CHO USER

👤 User: {display_name}
🆔 ID: {target_user_id}

Nhập số tiền muốn cộng (VND):

📝 Lưu ý:
• Số tiền > 0
• Dùng /cancel để hủy

Nhập số tiền:"""
        else:
            text = f"""💰 CỘNG TIỀN CHO USER

🆔 User ID: {target_user_id}
⚠️ User chưa từng sử dụng bot

Nhập số tiền muốn cộng (VND):

📝 Lưu ý:
• Số tiền > 0
• Dùng /cancel để hủy

Nhập số tiền:"""
        
        await update.message.reply_text(text)
    else:
        # Xóa state nếu không hợp lệ
        context.user_data.pop('waiting_for_user_id', None)
        await update.message.reply_text("❌ Có lỗi xảy ra! Vui lòng thử lại.")

async def handle_ban_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE, target_user_id: int):
    """Xử lý ban/unban user"""
    db = Database(DATABASE_FILE)
    
    # Kiểm tra user có tồn tại không
    user_info = db.get_user_info(target_user_id)
    if not user_info:
        await update.message.reply_text("❌ User không tồn tại trong hệ thống!")
        context.user_data.pop('waiting_for_user_id', None)
        return
    
    username, first_name = user_info[1], user_info[2]
    display_name = f"@{username}" if username else first_name or f"ID:{target_user_id}"
    
    # Kiểm tra trạng thái ban hiện tại
    is_banned = db.is_user_banned(target_user_id)
    
    if is_banned:
        # Unban user
        db.unban_user(target_user_id)
        await update.message.reply_text(f"✅ Đã UNBAN user {display_name} (ID: {target_user_id})")
        
        # Thông báo cho user
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="🎉 Tài khoản của bạn đã được mở khóa!\n\nBạn có thể sử dụng bot bình thường."
            )
        except:
            pass
    else:
        # Ban user
        db.ban_user(target_user_id)
        await update.message.reply_text(f"✅ Đã BAN user {display_name} (ID: {target_user_id})")
        
        # Thông báo cho user
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="🚫 Tài khoản của bạn đã bị khóa!\n\n📞 Liên hệ admin để được hỗ trợ."
            )
        except:
            pass
    
    # Xóa trạng thái chờ input
    context.user_data.pop('waiting_for_user_id', None)

async def process_balance_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input số tiền cộng cho user"""
    amount_input = update.message.text.strip()
    
    # Kiểm tra số tiền hợp lệ
    try:
        amount = int(amount_input)
        if amount <= 0:
            await update.message.reply_text("❌ Số tiền phải lớn hơn 0! Vui lòng nhập lại.")
            return
    except ValueError:
        await update.message.reply_text("❌ Số tiền không hợp lệ! Vui lòng nhập số.")
        return
    
    target_user_id = context.user_data.get('target_user_id')
    if not target_user_id:
        await update.message.reply_text("❌ Có lỗi xảy ra! Vui lòng thử lại.")
        context.user_data.clear()
        return
    
    # Cộng tiền cho user
    db = Database(DATABASE_FILE)
    db.update_balance(target_user_id, amount)
    
    # Thêm giao dịch vào lịch sử
    db.add_transaction(
        user_id=target_user_id,
        trans_type="admin_bonus",
        amount=amount,
        description=f"Admin cộng tiền",
        status="approved"
    )
    
    # Lấy thông tin user để hiển thị
    user_info = db.get_user_info(target_user_id)
    if user_info:
        username, first_name = user_info[1], user_info[2]
        display_name = f"@{username}" if username else first_name or f"ID:{target_user_id}"
    else:
        display_name = f"ID:{target_user_id}"
    
    new_balance = db.get_balance(target_user_id)
    
    await update.message.reply_text(
        f"✅ CỘNG TIỀN THÀNH CÔNG!\n\n"
        f"👤 User: {display_name}\n"
        f"💰 Đã cộng: {amount:,} VND\n"
        f"💳 Số dư mới: {new_balance:,} VND"
    )
    
    # Thông báo cho user
    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"🎉 NHẬN TIỀN THƯỞNG!\n\n"
                 f"💰 Bạn vừa nhận được: {amount:,} VND\n"
                 f"💳 Số dư hiện tại: {new_balance:,} VND\n\n"
                 f"Cảm ơn bạn đã sử dụng dịch vụ!"
        )
    except:
        pass
    
    # Xóa trạng thái chờ input
    context.user_data.pop('target_user_id', None)
    context.user_data.pop('waiting_for_balance_amount', None)

async def admin_view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin xem tất cả đơn hàng"""
    query = update.callback_query
    await query.answer()
    
    db = Database(DATABASE_FILE)
    orders = db.get_all_orders()
    
    if not orders:
        text = """📦 **QUẢN LÝ ĐƠN HÀNG**

❌ Chưa có đơn hàng nào trong hệ thống."""
    else:
        text = """📦 **QUẢN LÝ ĐƠN HÀNG**

📋 Danh sách đơn hàng gần đây:

"""
        
        for i, order in enumerate(orders[:20], 1):  # Hiển thị 20 đơn gần nhất
            order_id, user_id, username, first_name, email_quantity, total_amount, status, created_at = order
            
            # Tên hiển thị user
            if username:
                user_display = f"@{username}"
            elif first_name:
                user_display = first_name
            else:
                user_display = f"ID:{user_id}"
            
            # Kiểm tra đã nhận discount chưa
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT discount_amount FROM discounts WHERE order_id = ?', (order_id,))
            discount_record = cursor.fetchone()
            conn.close()
            
            discount_status = ""
            if discount_record:
                discount_status = f" (Đã claim: {discount_record[0]:,}đ)"
            else:
                discount_amount = db.get_discount_amount(email_quantity)
                if discount_amount > 0:
                    discount_status = f" (Có thể claim: {discount_amount:,}đ)"
            
            text += f"""**{i}. Order ID:** {order_id}
👤 User: {user_display} (ID: {user_id})
📧 Số lượng: {email_quantity} email
💰 Tổng tiền: {total_amount:,} VND
📅 Ngày: {created_at[:16]}{discount_status}

"""
    
    await query.edit_message_text(text, reply_markup=get_admin_users_keyboard(), parse_mode='Markdown')

# ==================== DISCOUNT MANAGEMENT HANDLERS ====================

async def admin_edit_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu chỉnh sửa mức chiết khấu"""
    query = update.callback_query
    await query.answer()
    
    text = """💸 **QUẢN LÝ MỨC CHIẾT KHẤU**

🎯 Bạn có thể:
• Xem bảng mức chiết khấu hiện tại
• Thêm/sửa mức chiết khấu theo số lượng email
• Xóa mức chiết khấu không cần thiết
• Khôi phục về cài đặt mặc định

💡 Chọn hành động bạn muốn thực hiện:"""
    
    await query.edit_message_text(text, reply_markup=get_admin_discount_keyboard(), parse_mode='Markdown')

async def admin_view_discount_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem bảng mức chiết khấu hiện tại"""
    query = update.callback_query
    await query.answer()
    
    text = settings_manager.get_discount_info_text()
    text += "\n\n💡 Sử dụng menu để chỉnh sửa mức chiết khấu."
    
    await query.edit_message_text(text, reply_markup=get_admin_discount_keyboard(), parse_mode='Markdown')

async def admin_add_discount_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bắt đầu quy trình thêm/sửa mức chiết khấu"""
    query = update.callback_query
    await query.answer()
    
    text = """➕ **THÊM/SỬA MỨC CHIẾT KHẤU**

📝 Nhập số lượng email (VD: 10, 20, 30...):

💡 **Lưu ý:**
• Nhập số nguyên dương
• Nếu số lượng đã tồn tại, mức chiết khấu sẽ được cập nhật
• Dùng /cancel để hủy

📩 Nhập số lượng email:"""
    
    context.user_data['waiting_for_discount_quantity'] = True
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_edit_discount"), parse_mode='Markdown')

async def admin_remove_discount_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bắt đầu quy trình xóa mức chiết khấu"""
    query = update.callback_query
    await query.answer()
    
    # Hiển thị các mức chiết khấu hiện có
    discount_rates = settings_manager.get_discount_rates()
    
    if not discount_rates:
        text = "❌ Không có mức chiết khấu nào để xóa."
        await query.edit_message_text(text, reply_markup=get_admin_discount_keyboard())
        return
    
    text = """➖ **XÓA MỨC CHIẾT KHẤU**

📋 Các mức chiết khấu hiện có:

"""
    
    sorted_rates = sorted(discount_rates.items(), key=lambda x: int(x[0]))
    for quantity, discount in sorted_rates:
        text += f"• {quantity} email → {discount:,} VND\n"
    
    text += """\n📝 Nhập số lượng email muốn xóa (VD: 10, 20...):

💡 Dùng /cancel để hủy

📩 Nhập số lượng email:"""
    
    context.user_data['waiting_for_remove_discount_quantity'] = True
    await query.edit_message_text(text, reply_markup=get_back_keyboard("admin_edit_discount"), parse_mode='Markdown')

async def admin_reset_discount_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Khôi phục mức chiết khấu về mặc định"""
    query = update.callback_query
    await query.answer()
    
    # Reset về default
    from settings_manager import DEFAULT_SETTINGS
    settings_manager.settings["discount_rates"] = DEFAULT_SETTINGS["discount_rates"].copy()
    settings_manager.save_settings()
    
    text = """🔄 **KHÔI PHỤC THÀNH CÔNG!**

✅ Đã khôi phục mức chiết khấu về cài đặt mặc định:

"""
    
    text += settings_manager.get_discount_info_text()
    
    await query.edit_message_text(text, reply_markup=get_admin_discount_keyboard(), parse_mode='Markdown')

# Discount input processors
async def process_discount_quantity_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input số lượng email cho chiết khấu"""
    quantity_input = update.message.text.strip()
    
    # Kiểm tra số lượng hợp lệ
    try:
        quantity = int(quantity_input)
        if quantity <= 0:
            await update.message.reply_text("❌ Số lượng email phải lớn hơn 0! Vui lòng nhập lại.")
            return
    except ValueError:
        await update.message.reply_text("❌ Vui lòng nhập số nguyên hợp lệ!")
        return
    
    # Lưu quantity và chuyển sang nhập discount amount
    context.user_data['discount_quantity'] = quantity
    context.user_data['waiting_for_discount_amount'] = True
    context.user_data.pop('waiting_for_discount_quantity', None)
    
    # Kiểm tra xem quantity đã có chưa
    current_rates = settings_manager.get_discount_rates()
    current_discount = current_rates.get(str(quantity), 0)
    
    if current_discount > 0:
        text = f"""💰 **CHỈNH SỬA MỨC CHIẾT KHẤU**

📧 Số lượng email: {quantity}
💰 Mức chiết khấu hiện tại: {current_discount:,} VND

💡 Nhập mức chiết khấu mới (VND):

📩 Nhập số tiền hoàn (VD: 15000):"""
    else:
        text = f"""➕ **THÊM MỨC CHIẾT KHẤU MỚI**

📧 Số lượng email: {quantity}

💡 Nhập mức chiết khấu (VND):

📩 Nhập số tiền hoàn (VD: 15000):"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def process_discount_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input số tiền chiết khấu"""
    amount_input = update.message.text.strip()
    
    # Kiểm tra số tiền hợp lệ
    try:
        amount = int(amount_input)
        if amount < 0:
            await update.message.reply_text("❌ Số tiền chiết khấu phải >= 0! Vui lòng nhập lại.")
            return
    except ValueError:
        await update.message.reply_text("❌ Vui lòng nhập số tiền hợp lệ!")
        return
    
    quantity = context.user_data.get('discount_quantity')
    if not quantity:
        await update.message.reply_text("❌ Có lỗi xảy ra! Vui lòng thử lại.")
        context.user_data.clear()
        return
    
    # Lưu mức chiết khấu mới
    success = settings_manager.set_discount_rate(quantity, amount)
    
    if success:
        if amount == 0:
            text = f"✅ **ĐÃ XÓA MỨC CHIẾT KHẤU**\n\n📧 Số lượng: {quantity} email\n💰 Không còn chiết khấu"
        else:
            text = f"✅ **CẬP NHẬT THÀNH CÔNG!**\n\n📧 Số lượng: {quantity} email\n💰 Mức chiết khấu: {amount:,} VND"
    else:
        text = "❌ **LỖI!** Không thể lưu cài đặt."
    
    await update.message.reply_text(text, parse_mode='Markdown')
    
    # Xóa trạng thái chờ input
    context.user_data.pop('discount_quantity', None)
    context.user_data.pop('waiting_for_discount_amount', None)

async def process_remove_discount_quantity_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input số lượng email cần xóa chiết khấu"""
    quantity_input = update.message.text.strip()
    
    # Kiểm tra số lượng hợp lệ
    try:
        quantity = int(quantity_input)
        if quantity <= 0:
            await update.message.reply_text("❌ Số lượng email phải lớn hơn 0! Vui lòng nhập lại.")
            return
    except ValueError:
        await update.message.reply_text("❌ Vui lòng nhập số nguyên hợp lệ!")
        return
    
    # Kiểm tra mức chiết khấu có tồn tại không
    current_rates = settings_manager.get_discount_rates()
    if str(quantity) not in current_rates:
        await update.message.reply_text(f"❌ Không tìm thấy mức chiết khấu cho {quantity} email!")
        return
    
    # Xóa mức chiết khấu
    success = settings_manager.remove_discount_rate(quantity)
    
    if success:
        text = f"✅ **ĐÃ XÓA THÀNH CÔNG!**\n\n📧 Đã xóa mức chiết khấu cho {quantity} email"
    else:
        text = "❌ **LỖI!** Không thể xóa mức chiết khấu."
    
    await update.message.reply_text(text, parse_mode='Markdown')
    
    # Xóa trạng thái chờ input
    context.user_data.pop('waiting_for_remove_discount_quantity', None)

async def admin_sheets_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem trạng thái Google Sheets"""
    query = update.callback_query
    await query.answer()
    
    try:
        sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
        status = sheets.get_sheet_status()
        
        if status["status"] == "connected":
            # Tính toán rate limit status
            rate_limit_info = ""
            if "write_count_in_window" in status:
                remaining = status.get("remaining_quota", 0)
                reset_time = status.get("window_reset_in", 0)
                
                if remaining < 10:
                    rate_limit_info = f"\n⚠️ **Rate Limit:** {remaining} requests còn lại"
                    if reset_time > 0:
                        rate_limit_info += f" (reset sau {reset_time:.0f}s)"
                else:
                    rate_limit_info = f"\n✅ **Rate Limit:** {remaining} requests khả dụng"
            
            text = f"""📊 **TRẠNG THÁI GOOGLE SHEETS**

✅ **Kết nối:** Thành công
📧 **Số lượng email:** {status['email_count']:,}
📄 **Sheet:** {status['sheet_title']}
🕒 **Cập nhật lần cuối:** {status['last_update']}{rate_limit_info}

💡 **Lưu ý về Rate Limit:**
• Google Sheets giới hạn 60 write requests/phút
• Hệ thống tự động delay 2 giây giữa các thao tác
• Nếu vượt quá, hệ thống sẽ retry sau 45-225 giây
• Batch size tự động giảm xuống 3 email/lần

⚠️ **Khuyến nghị:**
• Thêm email theo batch nhỏ (≤15 email/lần)
• Tránh thêm email liên tục trong thời gian ngắn
• Kiên nhẫn chờ khi có thông báo rate limit"""
            
        elif status["status"] == "error":
            text = f"""❌ **LỖI GOOGLE SHEETS**

🚫 **Trạng thái:** Lỗi kết nối
📧 **Số lượng email:** {status['email_count']}
⚠️ **Lỗi:** {status['error']}

💡 **Cách khắc phục:**
• Kiểm tra file credentials JSON
• Kiểm tra quyền truy cập Google Sheets
• Đảm bảo Sheet ID chính xác
• Thử kết nối lại sau vài phút"""
            
        else:
            text = """❌ **GOOGLE SHEETS KHÔNG KẾT NỐI**

🚫 **Trạng thái:** Chưa kết nối
📧 **Số lượng email:** Không xác định

💡 **Cần kiểm tra:**
• File credentials có tồn tại không
• Cấu hình trong config.py
• Quyền truy cập Google Drive API"""
        
    except Exception as e:
        text = f"""❌ **LỖI KIỂM TRA TRẠNG THÁI**

⚠️ **Lỗi:** {str(e)}

💡 **Cần kiểm tra:**
• Kết nối mạng
• Cấu hình Google Sheets
• File credentials JSON"""
    
    await query.edit_message_text(text, reply_markup=get_admin_emails_keyboard(), parse_mode='Markdown')
