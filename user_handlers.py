from telegram import Update
from telegram.ext import ContextTypes
import logging
from database import Database
from google_sheets import GoogleSheetsManager
from keyboards import *
from config import *
from settings_manager import settings_manager
import datetime

async def user_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu nạp tiền"""
    query = update.callback_query
    await query.answer()
    
    text = """💳 **NẠP TIỀN VÀO TÀI KHOẢN**

Chọn số tiền bạn muốn nạp:

💰 Tỷ lệ: 1 VND = 1 VND
📱 Hỗ trợ: Momo, Banking, Viettel Pay"""
    
    await query.edit_message_text(text, reply_markup=get_deposit_keyboard(), parse_mode='Markdown')

async def process_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý số tiền nạp"""
    query = update.callback_query
    await query.answer()
    
    # Lấy số tiền từ callback data
    if query.data.startswith('deposit_'):
        amount_str = query.data.split('_')[1]
        if amount_str == 'custom':
            text = """💰 **NẠP TIỀN CUSTOM**

Nhập số tiền bạn muốn nạp (VND):

📝 **Lưu ý:**
• Số tiền tối thiểu: 10,000 VND
• Số tiền tối đa: 10,000,000 VND
• Dùng /cancel để hủy

Nhập số tiền:"""
            
            context.user_data['waiting_for_deposit_amount'] = True
            await query.edit_message_text(text, reply_markup=get_back_keyboard("user_deposit"), parse_mode='Markdown')
            return
        
        try:
            amount = int(amount_str)
        except:
            await query.answer("❌ Số tiền không hợp lệ!")
            return
    else:
        return
    
    await show_deposit_info(query, context, amount)

async def process_custom_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý số tiền nạp custom"""
    if not context.user_data.get('waiting_for_deposit_amount'):
        return
    
    context.user_data['waiting_for_deposit_amount'] = False
    
    try:
        amount = int(update.message.text.replace(',', '').replace('.', ''))
        
        if amount < 10000:
            await update.message.reply_text("❌ Số tiền tối thiểu 10,000 VND!")
            return
        
        if amount > 10000000:
            await update.message.reply_text("❌ Số tiền tối đa 10,000,000 VND!")
            return
        
    except ValueError:
        await update.message.reply_text("❌ Vui lòng nhập số tiền hợp lệ!")
        return
    
    # Tạo message mới với thông tin nạp tiền
    text, keyboard = await get_deposit_info_text(update.effective_user.id, amount)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def show_deposit_info(query, context, amount):
    """Hiển thị thông tin chuyển khoản"""
    text, keyboard = await get_deposit_info_text(query.from_user.id, amount)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def get_deposit_info_text(user_id, amount):
    """Lấy text thông tin nạp tiền"""
    content = PAYMENT_INFO["content"].format(user_id=user_id)
    
    text = f"""💳 **THÔNG TIN CHUYỂN KHOẢN**

💰 **Số tiền:** {amount:,} VND

🏦 **Thông tin tài khoản:**
• Ngân hàng: {PAYMENT_INFO["bank_name"]}
• Số tài khoản: `{PAYMENT_INFO["account_number"]}`
• Chủ tài khoản: {PAYMENT_INFO["account_name"]}

📝 **Nội dung CK:** `{content}`

⚠️ **LưU Ý QUAN TRỌNG:**
• Chuyển khoản ĐÚNG số tiền: {amount:,} VND
• Ghi ĐÚNG nội dung: {content}
• Sau khi chuyển, nhấn "Đã chuyển khoản"
• Tiền sẽ được duyệt trong 1-5 phút

📞 Liên hệ admin nếu có vấn đề!"""
    
    keyboard = get_confirm_deposit_keyboard(amount)
    return text, keyboard

async def confirm_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xác nhận đã chuyển khoản"""
    query = update.callback_query
    await query.answer()
    
    amount = int(query.data.split('_')[2])
    user_id = query.from_user.id
    
    # Hiển thị thông báo chờ
    waiting_msg = await query.edit_message_text(
        "⏳ **Đang xử lý yêu cầu nạp tiền...**\n\n"
        "🔄 Hệ thống đang tạo giao dịch\n"
        "💫 Vui lòng chờ trong giây lát...",
        parse_mode='Markdown'
    )
    
    # Thêm giao dịch vào database
    db = Database(DATABASE_FILE)
    transaction_id = db.add_transaction(
        user_id=user_id,
        trans_type="deposit",
        amount=amount,
        description=f"Nạp tiền {amount:,} VND",
        status="pending"
    )
    
    # Cập nhật progress
    await waiting_msg.edit_text(
        "⏳ **Đang xử lý yêu cầu nạp tiền...**\n\n"
        "📨 Đang gửi thông báo cho admin\n"
        "💫 Vui lòng chờ trong giây lát...",
        parse_mode='Markdown'
    )
    
    # Thông báo cho admin
    for admin_id in ADMIN_IDS:
        try:
            user_info = query.from_user
            user_name = user_info.username or user_info.first_name or f"User {user_id}"
            
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"💰 **NẠP TIỀN MỚI**\n\n"
                     f"👤 User: {user_name} (`{user_id}`)\n"
                     f"💰 Số tiền: {amount:,} VND\n"
                     f"📅 Thời gian: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                     f"🆔 Transaction ID: {transaction_id}",
                reply_markup=get_admin_deposit_approval_keyboard(transaction_id),
                parse_mode='Markdown'
            )
        except Exception as e:
            logging.error(f"Lỗi gửi thông báo admin: {e}")
    
    text = f"""✅ **ĐÃ GỬI YÊU CẦU NẠP TIỀN**

💰 **Số tiền:** {amount:,} VND
🆔 **Mã GD:** {transaction_id}

⏳ Giao dịch đang chờ admin duyệt
📱 Bạn sẽ nhận được thông báo khi được duyệt
⚡ Thời gian duyệt: 1-5 phút

📞 Liên hệ admin nếu quá 10 phút chưa được duyệt!"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("user_back"), parse_mode='Markdown')

async def user_buy_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu mua email"""
    query = update.callback_query
    await query.answer()
    
    # Kiểm tra số lượng email trong kho
    try:
        sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
        email_count = sheets.get_email_count()
    except:
        email_count = 0
    
    if email_count == 0:
        text = """❌ **HẾT HÀNG**

Hiện tại kho email đã hết hàng!
Vui lòng quay lại sau hoặc liên hệ admin."""
        await query.edit_message_text(text, reply_markup=get_back_keyboard("user_back"), parse_mode='Markdown')
        return
    
    product_price = settings_manager.get_product_price()
    product_name = settings_manager.get_product_name()
    
    text = f"""📧 MUA {product_name.upper()}

💰 Giá: {product_price:,} VND/email
📦 Có sẵn: {email_count} email
✨ Chất lượng: Gmail mới, chưa sử dụng

Chọn số lượng email bạn muốn mua:"""
    
    await query.edit_message_text(text, reply_markup=get_buy_email_keyboard())

async def process_buy_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý mua email"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('buy_email_'):
        quantity_str = query.data.split('_')[2]
        
        if quantity_str == 'custom':
            text = """📧 **MUA EMAIL CUSTOM**

Nhập số lượng email bạn muốn mua:

📝 **Lưu ý:**
• Số lượng tối thiểu: 1 email
• Số lượng tối đa: 50 email/lần
• Dùng /cancel để hủy

Nhập số lượng:"""
            
            context.user_data['waiting_for_email_quantity'] = True
            await query.edit_message_text(text, reply_markup=get_back_keyboard("user_buy_email"), parse_mode='Markdown')
            return
        
        try:
            quantity = int(quantity_str)
        except:
            await query.answer("❌ Số lượng không hợp lệ!")
            return
    else:
        return
    
    await show_purchase_confirmation(query, context, quantity)

async def process_custom_email_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý số lượng email custom"""
    if not context.user_data.get('waiting_for_email_quantity'):
        return
    
    context.user_data['waiting_for_email_quantity'] = False
    
    try:
        quantity = int(update.message.text)
        
        if quantity < 1:
            await update.message.reply_text("❌ Số lượng tối thiểu 1 email!")
            return
        
        if quantity > 50:
            await update.message.reply_text("❌ Số lượng tối đa 50 email/lần!")
            return
        
    except ValueError:
        await update.message.reply_text("❌ Vui lòng nhập số lượng hợp lệ!")
        return
    
    # Tạo message mới với xác nhận mua
    text, keyboard = await get_purchase_confirmation_text(update.effective_user.id, quantity)
    await update.message.reply_text(text, reply_markup=keyboard)

async def show_purchase_confirmation(query, context, quantity):
    """Hiển thị xác nhận mua email"""
    text, keyboard = await get_purchase_confirmation_text(query.from_user.id, quantity)
    await query.edit_message_text(text, reply_markup=keyboard)

async def get_purchase_confirmation_text(user_id, quantity):
    """Lấy text xác nhận mua email"""
    product_price = settings_manager.get_product_price()
    product_name = settings_manager.get_product_name()
    total_price = quantity * product_price
    
    # Kiểm tra số dư
    db = Database(DATABASE_FILE)
    balance = db.get_balance(user_id)
    
    # Kiểm tra kho
    try:
        sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
        email_count = sheets.get_email_count()
    except:
        email_count = 0
    
    text = f"""📧 XÁC NHẬN MUA {product_name.upper()}

📦 Số lượng: {quantity} email
💰 Tổng tiền: {total_price:,} VND
💳 Số dư của bạn: {balance:,} VND

"""
    
    if balance < total_price:
        text += f"❌ Số dư không đủ!\nBạn cần nạp thêm {total_price - balance:,} VND"
        keyboard = get_back_keyboard("user_buy_email")
    elif email_count < quantity:
        text += f"❌ Kho không đủ!\nChỉ còn {email_count} email"
        keyboard = get_back_keyboard("user_buy_email")
    else:
        text += "✅ Đủ điều kiện mua hàng!"
        keyboard = get_confirm_purchase_keyboard(quantity, total_price)
    
    return text, keyboard

async def confirm_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xác nhận mua email"""
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.split('_')
    quantity = int(data_parts[2])
    total_price = int(data_parts[3])
    user_id = query.from_user.id
    
    db = Database(DATABASE_FILE)
    
    # Kiểm tra lại số dư
    balance = db.get_balance(user_id)
    if balance < total_price:
        await query.edit_message_text("❌ **Số dư không đủ!**", reply_markup=get_back_keyboard("user_buy_email"), parse_mode='Markdown')
        return
    
    # Hiển thị thông báo chờ
    waiting_msg = await query.edit_message_text(
        "⏳ **Đang xử lý đơn hàng...**\n\n"
        "🔄 Hệ thống đang lấy email từ kho\n"
        "💫 Vui lòng chờ trong giây lát...",
        parse_mode='Markdown'
    )
    
    # Mua email từ Google Sheets
    try:
        sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID)
        purchased_emails = []
        
        for i in range(quantity):
            # Cập nhật progress
            await waiting_msg.edit_text(
                f"⏳ **Đang xử lý đơn hàng...**\n\n"
                f"🔄 Đang lấy email {i+1}/{quantity}\n"
                f"💫 Vui lòng chờ trong giây lát...",
                parse_mode='Markdown'
            )
            
            email_data = sheets.purchase_email()
            if email_data:
                email, password = email_data
                purchased_emails.append((email, password))
                
                # Lưu vào database
                product_price = settings_manager.get_product_price()
                db.add_purchase(user_id, email, password, product_price)
            else:
                break
        
        if not purchased_emails:
            await query.edit_message_text("❌ Lỗi: Không thể lấy email từ kho!", reply_markup=get_back_keyboard("user_buy_email"))
            return
        
        # Trừ tiền
        actual_quantity = len(purchased_emails)
        actual_total = actual_quantity * product_price
        db.update_balance(user_id, -actual_total)
        
        # Tạo đơn hàng với Order ID
        order_id = db.create_order(user_id, actual_quantity, actual_total)
        
        # Thêm giao dịch
        db.add_transaction(
            user_id=user_id,
            trans_type="purchase",
            amount=-actual_total,
            description=f"Mua {actual_quantity} email Gmail - Order: {order_id}",
            status="approved"
        )
        
        # Tạo message với danh sách email
        product_name = settings_manager.get_product_name()
        
        # Tính discount có thể nhận
        discount_amount = db.get_discount_amount(actual_quantity)
        
        text = f"""✅ MUA {product_name.upper()} THÀNH CÔNG!

🆔 Order ID: {order_id}
📦 Đã mua: {actual_quantity} email
💰 Tổng tiền: {actual_total:,} VND
💳 Số dư còn lại: {balance - actual_total:,} VND

📧 DANH SÁCH EMAIL:

"""
        
        for i, (email, password) in enumerate(purchased_emails, 1):
            text += f"{i}. {email}:{password}\n"
        
        text += f"\n⚠️ Lưu ý: Vui lòng sao chép và lưu email ngay!"
        
        # Hiển thị thông tin discount nếu đủ điều kiện
        if discount_amount > 0:
            text += f"\n\n🎉 KHUYẾN MẠI!\n💰 Đơn hàng này đủ điều kiện nhận hoàn tiền {discount_amount:,} VND\n📱 Sử dụng Order ID: {order_id} trong menu 'Chiết khấu' để nhận tiền!"
        
        await query.edit_message_text(text, reply_markup=get_back_keyboard("user_back"))
        
    except Exception as e:
        logging.error(f"Lỗi mua email: {e}")
        await query.edit_message_text("❌ Lỗi hệ thống! Vui lòng thử lại sau.", reply_markup=get_back_keyboard("user_buy_email"))

async def user_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu tài khoản user"""
    query = update.callback_query
    await query.answer()
    
    text = """👤 **TÀI KHOẢN CỦA BẠN**

Chọn thông tin bạn muốn xem:"""
    
    await query.edit_message_text(text, reply_markup=get_user_account_keyboard(), parse_mode='Markdown')

async def user_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem số dư"""
    query = update.callback_query
    await query.answer()
    
    db = Database(DATABASE_FILE)
    balance = db.get_balance(query.from_user.id)
    
    product_price = settings_manager.get_product_price()
    product_name = settings_manager.get_product_name()
    
    text = f"""💰 SỐ DƯ TÀI KHOẢN

💳 Số dư hiện tại: {balance:,} VND

📊 Thông tin:
• 1 {product_name} = {product_price:,} VND
• Có thể mua được: {balance // product_price} email

💡 Lưu ý: Nạp tiền để mua thêm email!"""
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("user_account"))

async def user_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem lịch sử giao dịch"""
    query = update.callback_query
    await query.answer()
    
    db = Database(DATABASE_FILE)
    transactions = db.get_user_transactions(query.from_user.id)
    
    if not transactions:
        text = "📜 **LỊCH SỬ GIAO DỊCH**\n\n❌ Chưa có giao dịch nào!"
    else:
        text = "📜 **LỊCH SỬ GIAO DỊCH**\n\n"
        
        for trans in transactions:
            trans_type, amount, description, status, created_at = trans
            
            if trans_type == "deposit":
                icon = "💳"
                amount_text = f"+{amount:,} VND"
            else:
                icon = "📧"
                amount_text = f"{amount:,} VND"
            
            status_icon = "✅" if status == "approved" else "⏳" if status == "pending" else "❌"
            
            text += f"{icon} **{description}**\n"
            text += f"💰 {amount_text} {status_icon}\n"
            text += f"📅 {created_at[:16]}\n\n"
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("user_account"), parse_mode='Markdown')

async def user_purchases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem email đã mua"""
    query = update.callback_query
    await query.answer()
    
    db = Database(DATABASE_FILE)
    purchases = db.get_user_purchases(query.from_user.id)
    
    if not purchases:
        text = "📧 **EMAIL ĐÃ MUA**\n\n❌ Chưa mua email nào!"
    else:
        text = "📧 **EMAIL ĐÃ MUA** (10 gần nhất)\n\n"
        
        for i, purchase in enumerate(purchases, 1):
            email, password, price, created_at = purchase
            text += f"`{i}.` {email}:{password}\n"
            text += f"💰 {price:,} VND | 📅 {created_at[:10]}\n\n"
    
    await query.edit_message_text(text, reply_markup=get_back_keyboard("user_account"), parse_mode='Markdown')

async def user_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Thông tin liên hệ"""
    query = update.callback_query
    await query.answer()
    
    # Lấy message liên hệ từ settings
    contact_text = settings_manager.get_contact_message()
    
    await query.edit_message_text(contact_text, reply_markup=get_back_keyboard("user_back"))

async def user_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quay lại menu user"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        MESSAGES["user_welcome"],
        reply_markup=get_main_keyboard(is_admin=False)
    )

# ==================== DISCOUNT HANDLERS ====================

async def user_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu chiết khấu user"""
    query = update.callback_query
    await query.answer()
    
    # Lấy thông tin chiết khấu động từ settings
    discount_rates = settings_manager.get_discount_rates()
    
    text = """💸 **CHIẾT KHẤU ĐƠN HÀNG**

🎁 Nhận hoàn tiền khi mua số lượng email lớn!

📊 **Bảng mức chiết khấu:**
"""
    
    if discount_rates:
        sorted_rates = sorted(discount_rates.items(), key=lambda x: int(x[0]))
        for quantity, discount in sorted_rates:
            text += f"• {quantity} email = hoàn {discount:,} VND\n"
    else:
        text += "• Hiện tại chưa có chương trình chiết khấu\n"
    
    text += "\n💡 Sử dụng Order ID từ đơn hàng để nhận chiết khấu!"
    
    await query.edit_message_text(text, reply_markup=get_user_discount_keyboard(), parse_mode='Markdown')

async def user_claim_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bắt đầu quy trình nhận chiết khấu"""
    query = update.callback_query
    await query.answer()
    
    text = """💸 **NHẬN CHIẾT KHẤU**

📝 Nhập Order ID của đơn hàng bạn muốn áp dụng chiết khấu:

💡 **Lưu ý:**
• Order ID có dạng: ORD12345678
• Mỗi đơn hàng chỉ được nhận chiết khấu 1 lần
• Chỉ chủ đơn hàng mới có thể nhận chiết khấu

📱 Nhập Order ID hoặc /cancel để hủy:"""
    
    context.user_data['waiting_for_order_id'] = True
    await query.edit_message_text(text, reply_markup=get_back_keyboard("user_discount"), parse_mode='Markdown')

async def user_discount_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị bảng mức chiết khấu"""
    query = update.callback_query
    await query.answer()
    
    # Lấy bảng mức chiết khấu từ settings
    text = settings_manager.get_discount_info_text()
    
    text += """\n⚡ **Cách nhận:**
1. Mua email với số lượng đủ điều kiện
2. Lưu Order ID từ kết quả mua hàng
3. Vào menu "💸 Chiết khấu" → "💸 Nhận chiết khấu"
4. Nhập Order ID và nhận tiền ngay!

💡 **Lưu ý:** Mỗi đơn hàng chỉ được áp dụng chiết khấu 1 lần."""
    
    await query.edit_message_text(text, reply_markup=get_user_discount_keyboard(), parse_mode='Markdown')

async def user_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem danh sách đơn hàng của user"""
    query = update.callback_query
    await query.answer()
    
    db = Database(DATABASE_FILE)
    orders = db.get_user_orders(query.from_user.id)
    
    if not orders:
        text = """📦 **ĐƠN HÀNG CỦA TÔI**

❌ Bạn chưa có đơn hàng nào."""
    else:
        text = """📦 **ĐƠN HÀNG CỦA TÔI**

📋 Danh sách đơn hàng gần đây:

"""
        for i, order in enumerate(orders[:10], 1):  # Chỉ hiển thị 10 đơn gần nhất
            order_id, email_quantity, total_amount, status, created_at = order
            
            # Kiểm tra đã nhận discount chưa
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT discount_amount FROM discounts WHERE order_id = ?', (order_id,))
            discount_record = cursor.fetchone()
            conn.close()
            
            discount_status = ""
            if discount_record:
                discount_status = f" (Đã nhận chiết khấu: {discount_record[0]:,} VND)"
            else:
                discount_amount = db.get_discount_amount(email_quantity)
                if discount_amount > 0:
                    discount_status = f" (Có thể nhận: {discount_amount:,} VND)"
            
            text += f"""**{i}. Order ID:** {order_id}
📧 Số lượng: {email_quantity} email
💰 Tổng tiền: {total_amount:,} VND
📅 Ngày: {created_at[:16]}{discount_status}

"""
    
    await query.edit_message_text(text, reply_markup=get_user_account_keyboard(), parse_mode='Markdown')

async def process_order_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input Order ID cho chiết khấu"""
    if not context.user_data.get('waiting_for_order_id'):
        return
    
    order_id = update.message.text.strip().upper()
    user_id = update.effective_user.id
    
    # Xóa trạng thái chờ input
    context.user_data.pop('waiting_for_order_id', None)
    
    # Kiểm tra format Order ID
    if not order_id.startswith('ORD') or len(order_id) != 11:
        await update.message.reply_text("❌ Order ID không đúng định dạng!\nOrder ID phải có dạng: ORD12345678")
        return
    
    db = Database(DATABASE_FILE)
    
    # Hiển thị thông báo chờ
    processing_msg = await update.message.reply_text(
        "⏳ **Đang xử lý yêu cầu chiết khấu...**\n\n"
        "🔄 Kiểm tra Order ID và điều kiện\n"
        "💫 Vui lòng chờ trong giây lát...",
        parse_mode='Markdown'
    )
    
    # Kiểm tra điều kiện và thực hiện chiết khấu
    result = db.claim_discount(order_id, user_id)
    
    if result.get('success'):
        discount_amount = result['discount_amount']
        new_balance = db.get_balance(user_id)
        
        text = f"""✅ **NHẬN CHIẾT KHẤU THÀNH CÔNG!**

🆔 Order ID: {order_id}
💰 Số tiền nhận được: {discount_amount:,} VND
💳 Số dư mới: {new_balance:,} VND

🎉 Cảm ơn bạn đã sử dụng dịch vụ!"""
        
    else:
        error_msg = result.get('error', 'Có lỗi xảy ra!')
        text = f"❌ **KHÔNG THỂ NHẬN CHIẾT KHẤU**\n\n{error_msg}"
    
    await processing_msg.edit_text(text, parse_mode='Markdown')
