import sqlite3
import datetime
import uuid
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_file)
    
    def init_database(self):
        """Khởi tạo các bảng database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Bảng users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_banned INTEGER DEFAULT 0
            )
        ''')
        
        # Bảng transactions (giao dịch)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,  -- 'deposit', 'purchase', 'admin_add'
                amount INTEGER,
                description TEXT,
                status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Bảng purchases (lịch sử mua email)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                email TEXT,
                password TEXT,
                price INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Bảng orders (đơn hàng với ID duy nhất)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                email_quantity INTEGER,
                total_amount INTEGER,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Bảng discounts (lịch sử chiết khấu)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT,
                user_id INTEGER,
                discount_amount INTEGER,
                claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (order_id) REFERENCES orders (order_id)
            )
        ''')
        
        # Bảng settings (cài đặt hệ thống)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Thêm user mới"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Tuple]:
        """Lấy thông tin user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def update_balance(self, user_id: int, amount: int):
        """Cập nhật số dư user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET balance = balance + ? WHERE user_id = ?
        ''', (amount, user_id))
        
        conn.commit()
        conn.close()
    
    def get_balance(self, user_id: int) -> int:
        """Lấy số dư user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else 0
    
    def add_transaction(self, user_id: int, trans_type: str, amount: int, description: str = "", status: str = "pending"):
        """Thêm giao dịch"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, description, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, trans_type, amount, description, status))
        
        transaction_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return transaction_id
    
    def get_pending_deposits(self) -> List[Tuple]:
        """Lấy danh sách nạp tiền chờ duyệt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.id, t.user_id, u.username, u.first_name, t.amount, t.created_at
            FROM transactions t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.type = 'deposit' AND t.status = 'pending'
            ORDER BY t.created_at ASC
        ''')
        
        deposits = cursor.fetchall()
        conn.close()
        return deposits
    
    def approve_deposit(self, transaction_id: int):
        """Duyệt nạp tiền"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Lấy thông tin giao dịch
        cursor.execute('SELECT user_id, amount FROM transactions WHERE id = ?', (transaction_id,))
        result = cursor.fetchone()
        
        if result:
            user_id, amount = result
            
            # Cập nhật trạng thái giao dịch
            cursor.execute('UPDATE transactions SET status = ? WHERE id = ?', ('approved', transaction_id))
            
            # Cộng tiền vào tài khoản
            cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
            
            conn.commit()
        
        conn.close()
        return result is not None
    
    def reject_deposit(self, transaction_id: int):
        """Từ chối nạp tiền"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE transactions SET status = ? WHERE id = ?', ('rejected', transaction_id))
        
        conn.commit()
        conn.close()
    
    def add_purchase(self, user_id: int, email: str, password: str, price: int):
        """Thêm lịch sử mua email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO purchases (user_id, email, password, price)
            VALUES (?, ?, ?, ?)
        ''', (user_id, email, password, price))
        
        conn.commit()
        conn.close()
    
    def get_user_transactions(self, user_id: int) -> List[Tuple]:
        """Lấy lịch sử giao dịch của user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT type, amount, description, status, created_at
            FROM transactions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 20
        ''', (user_id,))
        
        transactions = cursor.fetchall()
        conn.close()
        return transactions
    
    def get_user_purchases(self, user_id: int) -> List[Tuple]:
        """Lấy lịch sử mua email của user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, password, price, created_at
            FROM purchases
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id,))
        
        purchases = cursor.fetchall()
        conn.close()
        return purchases
    
    def get_stats(self) -> dict:
        """Lấy thống kê hệ thống"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tổng số user
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Tổng doanh thu (từ purchases)
        cursor.execute('SELECT SUM(price) FROM purchases')
        total_revenue = cursor.fetchone()[0] or 0
        
        # Tổng tiền nạp đã duyệt
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "deposit" AND status = "approved"')
        total_deposits = cursor.fetchone()[0] or 0
        
        # Thống kê hôm nay
        today = datetime.date.today().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?', (today,))
        new_users_today = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(price) FROM purchases WHERE DATE(created_at) = ?', (today,))
        revenue_today = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_revenue': total_revenue,
            'total_deposits': total_deposits,
            'new_users_today': new_users_today,
            'revenue_today': revenue_today
        }
    
    def get_all_users(self) -> List[Tuple]:
        """Lấy danh sách tất cả user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, username, first_name, balance, created_at, is_banned FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def ban_user(self, user_id: int):
        """Ban user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def unban_user(self, user_id: int):
        """Unban user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def is_user_banned(self, user_id: int) -> bool:
        """Kiểm tra user có bị ban không"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_banned FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result and result[0] == 1
    
    def get_user_info(self, user_id: int) -> tuple:
        """Lấy thông tin user (user_id, username, first_name, balance, is_banned)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, username, first_name, balance, is_banned FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result
    
    def generate_order_id(self) -> str:
        """Tạo Order ID duy nhất"""
        return f"ORD{uuid.uuid4().hex[:8].upper()}"
    
    def create_order(self, user_id: int, email_quantity: int, total_amount: int) -> str:
        """Tạo đơn hàng mới và trả về Order ID"""
        order_id = self.generate_order_id()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (order_id, user_id, email_quantity, total_amount)
            VALUES (?, ?, ?, ?)
        ''', (order_id, user_id, email_quantity, total_amount))
        
        conn.commit()
        conn.close()
        
        return order_id
    
    def get_order_info(self, order_id: str) -> tuple:
        """Lấy thông tin đơn hàng"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT order_id, user_id, email_quantity, total_amount, status, created_at
            FROM orders WHERE order_id = ?
        ''', (order_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result
    
    def get_user_orders(self, user_id: int) -> list:
        """Lấy danh sách đơn hàng của user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT order_id, email_quantity, total_amount, status, created_at
            FROM orders WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        results = cursor.fetchall()
        
        conn.close()
        return results
    
    def get_discount_amount(self, email_quantity: int) -> int:
        """Tính số tiền chiết khấu theo số lượng email - sử dụng settings_manager"""
        from settings_manager import settings_manager
        return settings_manager.get_discount_amount(email_quantity)
    
    def check_discount_eligibility(self, order_id: str, user_id: int) -> dict:
        """Kiểm tra điều kiện chiết khấu"""
        # Lấy thông tin đơn hàng
        order_info = self.get_order_info(order_id)
        if not order_info:
            return {"eligible": False, "error": "Đơn hàng không tồn tại"}
        
        order_user_id = order_info[1]
        email_quantity = order_info[2]
        
        # Kiểm tra user có phải chủ đơn hàng
        if order_user_id != user_id:
            return {"eligible": False, "error": "Bạn không phải chủ đơn hàng này"}
        
        # Kiểm tra đã claim chiết khấu chưa
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM discounts WHERE order_id = ?', (order_id,))
        if cursor.fetchone():
            conn.close()
            return {"eligible": False, "error": "Đơn hàng này đã được sử dụng chiết khấu"}
        conn.close()
        
        # Tính số tiền chiết khấu
        discount_amount = self.get_discount_amount(email_quantity)
        if discount_amount == 0:
            return {"eligible": False, "error": f"Đơn hàng có {email_quantity} email chưa đủ điều kiện chiết khấu (tối thiểu 10 email)"}
        
        return {
            "eligible": True,
            "discount_amount": discount_amount,
            "email_quantity": email_quantity,
            "order_id": order_id
        }
    
    def claim_discount(self, order_id: str, user_id: int) -> dict:
        """Nhận chiết khấu"""
        # Kiểm tra điều kiện
        eligibility = self.check_discount_eligibility(order_id, user_id)
        if not eligibility["eligible"]:
            return eligibility
        
        discount_amount = eligibility["discount_amount"]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Thêm record chiết khấu
            cursor.execute('''
                INSERT INTO discounts (order_id, user_id, discount_amount)
                VALUES (?, ?, ?)
            ''', (order_id, user_id, discount_amount))
            
            # Cộng tiền vào tài khoản
            cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', 
                         (discount_amount, user_id))
            
            # Thêm transaction history
            cursor.execute('''
                INSERT INTO transactions (user_id, type, amount, description, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, "discount", discount_amount, f"Chiết khấu đơn hàng {order_id}", "approved"))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "discount_amount": discount_amount,
                "order_id": order_id
            }
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"success": False, "error": f"Lỗi xử lý: {str(e)}"}
    
    def get_all_orders(self) -> list:
        """Lấy tất cả đơn hàng (cho admin)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.order_id, o.user_id, u.username, u.first_name, 
                   o.email_quantity, o.total_amount, o.status, o.created_at
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            ORDER BY o.created_at DESC
        ''', )
        results = cursor.fetchall()
        
        conn.close()
        return results
