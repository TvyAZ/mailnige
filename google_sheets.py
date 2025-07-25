import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import time
from typing import List, Optional, Tuple

class GoogleSheetsManager:
    def __init__(self, credentials_file: str, sheet_id: str):
        self.credentials_file = credentials_file
        self.sheet_id = sheet_id
        self.client = None
        self.worksheet = None
        self.last_write_time = 0
        self.write_delay = 2.0  # Tăng delay lên 2 giây để an toàn hơn
        self.max_retries = 5  # Tăng số lần retry
        self.write_count = 0  # Đếm số lần write trong 1 phút
        self.write_window_start = time.time()  # Thời điểm bắt đầu cửa sổ 1 phút
        self.connect()
    
    def connect(self):
        """Kết nối đến Google Sheets"""
        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
            self.client = gspread.authorize(credentials)
            
            # Mở sheet và lấy worksheet đầu tiên
            sheet = self.client.open_by_key(self.sheet_id)
            self.worksheet = sheet.get_worksheet(0)  # Lấy sheet đầu tiên
            
            logging.info("Đã kết nối thành công đến Google Sheets")
            
        except Exception as e:
            logging.error(f"Lỗi kết nối Google Sheets: {e}")
            self.client = None
            self.worksheet = None
    
    def wait_for_rate_limit(self):
        """Chờ để tránh rate limit - cải tiến với rate limiting window"""
        current_time = time.time()
        
        # Reset counter nếu đã qua 1 phút
        if current_time - self.write_window_start >= 60:
            self.write_count = 0
            self.write_window_start = current_time
        
        # Nếu đã viết quá 50 lần trong 1 phút, chờ đến phút tiếp theo
        if self.write_count >= 50:  # Giới hạn 50 thay vì 60 để an toàn
            wait_time = 60 - (current_time - self.write_window_start) + 5  # +5 giây buffer
            if wait_time > 0:
                logging.warning(f"Rate limit protection: waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)
                # Reset counter sau khi chờ
                self.write_count = 0
                self.write_window_start = time.time()
        
        # Delay bình thường giữa các request
        time_since_last_write = current_time - self.last_write_time
        if time_since_last_write < self.write_delay:
            sleep_time = self.write_delay - time_since_last_write
            time.sleep(sleep_time)
        
        self.last_write_time = time.time()
        self.write_count += 1
    
    def execute_with_retry(self, operation, *args, **kwargs):
        """Thực hiện operation với retry logic cho rate limit"""
        for attempt in range(self.max_retries):
            try:
                self.wait_for_rate_limit()
                return operation(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                if 'quota exceeded' in error_str or 'rate_limit_exceeded' in error_str or '429' in error_str or 'limit exceeded' in error_str:
                    if attempt < self.max_retries - 1:
                        wait_time = min((attempt + 1) * 45, 300)  # 45, 90, 135, 180, 225 giây, max 5 phút
                        logging.warning(f"Rate limit exceeded, retrying in {wait_time} seconds... (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        # Reset write counter để tránh rate limit tiếp theo
                        self.write_count = 0
                        self.write_window_start = time.time()
                        continue
                    else:
                        logging.error(f"Rate limit exceeded after {self.max_retries} attempts")
                        raise e
                else:
                    # Lỗi khác, không retry
                    raise e
        
        return None

    def get_first_email(self) -> Optional[Tuple[str, str]]:
        """Lấy email đầu tiên trong sheet (được thêm vào sớm nhất)"""
        if not self.worksheet:
            return None
        
        try:
            # Lấy tất cả dữ liệu
            all_records = self.worksheet.get_all_records()
            
            if not all_records:
                return None
            
            # Lấy record đầu tiên (email được thêm vào sớm nhất)
            first_record = all_records[0]
            
            # Kiểm tra định dạng email:password
            if 'Email' in first_record and 'Password' in first_record:
                email = first_record['Email']
                password = first_record['Password']
                return (email, password)
            
            # Nếu không có column header, thử lấy từ cell
            cells = self.worksheet.row_values(2)  # Row 2 (bỏ qua header)
            if len(cells) >= 2:
                email_pass = cells[0].split(':') if ':' in cells[0] else [cells[0], cells[1] if len(cells) > 1 else '']
                if len(email_pass) == 2:
                    return (email_pass[0], email_pass[1])
                
        except Exception as e:
            logging.error(f"Lỗi lấy email từ Google Sheets: {e}")
        
        return None
    
    def delete_first_email(self):
        """Xóa email đầu tiên trong sheet với retry logic"""
        if not self.worksheet:
            return False
        
        try:
            # Sử dụng retry logic cho delete operation
            self.execute_with_retry(self.worksheet.delete_rows, 2)
            logging.info("Đã xóa email đầu tiên từ Google Sheets")
            return True
            
        except Exception as e:
            logging.error(f"Lỗi xóa email từ Google Sheets: {e}")
            return False
    
    def add_emails(self, emails: List[str]) -> int:
        """Thêm nhiều email vào sheet với rate limit handling"""
        if not self.worksheet:
            return 0
        
        try:
            added_count = 0
            for email_line in emails:
                if ':' in email_line:
                    email, password = email_line.split(':', 1)
                    # Sử dụng retry logic cho append operation
                    self.execute_with_retry(self.worksheet.append_row, [email.strip(), password.strip()])
                    added_count += 1
            
            logging.info(f"Đã thêm {added_count} email vào Google Sheets")
            return added_count
            
        except Exception as e:
            logging.error(f"Lỗi thêm email vào Google Sheets: {e}")
            return 0
    
    def add_emails_batch(self, emails: List[str], batch_size: int = 3) -> int:
        """Thêm nhiều email vào sheet theo batch để tránh rate limit"""
        if not self.worksheet:
            return 0
        
        try:
            added_count = 0
            email_rows = []
            
            # Chuẩn bị dữ liệu
            for email_line in emails:
                if ':' in email_line:
                    email, password = email_line.split(':', 1)
                    email_rows.append([email.strip(), password.strip()])
            
            # Thêm theo batch
            for i in range(0, len(email_rows), batch_size):
                batch = email_rows[i:i + batch_size]
                if batch:
                    # Sử dụng retry logic cho batch operation
                    self.execute_with_retry(self.worksheet.append_rows, batch)
                    added_count += len(batch)
                    logging.info(f"Đã thêm batch {len(batch)} email vào Google Sheets")
            
            logging.info(f"Hoàn thành thêm {added_count} email vào Google Sheets")
            return added_count
            
        except Exception as e:
            logging.error(f"Lỗi thêm batch email vào Google Sheets: {e}")
            return added_count  # Trả về số lượng đã thêm thành công
    
    def get_email_count(self) -> int:
        """Lấy số lượng email trong sheet"""
        if not self.worksheet:
            return 0
        
        try:
            all_records = self.worksheet.get_all_records()
            return len(all_records)
            
        except Exception as e:
            logging.error(f"Lỗi đếm email trong Google Sheets: {e}")
            return 0
    
    def setup_sheet_headers(self):
        """Thiết lập header cho sheet nếu chưa có"""
        if not self.worksheet:
            return False
        
        try:
            # Kiểm tra xem có header chưa
            first_row = self.worksheet.row_values(1)
            
            if not first_row or first_row[0] != 'Email':
                # Thêm header
                self.worksheet.update('A1:B1', [['Email', 'Password']])
                logging.info("Đã thiết lập header cho Google Sheets")
            
            return True
            
        except Exception as e:
            logging.error(f"Lỗi thiết lập header Google Sheets: {e}")
            return False
    
    def purchase_email(self) -> Optional[Tuple[str, str]]:
        """Mua email - lấy và xóa email đầu tiên"""
        email_data = self.get_first_email()
        if email_data:
            if self.delete_first_email():
                return email_data
        return None
    
    def get_all_emails_preview(self, limit: int = 10) -> List[Tuple[str, str]]:
        """Lấy danh sách email để preview (không xóa)"""
        if not self.worksheet:
            return []
        
        try:
            all_records = self.worksheet.get_all_records()
            emails = []
            
            for i, record in enumerate(all_records[:limit]):
                if 'Email' in record and 'Password' in record:
                    emails.append((record['Email'], record['Password']))
                elif len(all_records[0]) >= 2:
                    # Fallback nếu không có header
                    row_values = self.worksheet.row_values(i + 2)  # +2 vì bắt đầu từ row 2
                    if len(row_values) >= 2:
                        emails.append((row_values[0], row_values[1]))
            
            return emails
            
        except Exception as e:
            logging.error(f"Lỗi lấy preview email từ Google Sheets: {e}")
            return []
    
    def get_sheet_status(self) -> dict:
        """Lấy thông tin trạng thái sheet"""
        try:
            if not self.worksheet:
                return {"status": "disconnected", "email_count": 0, "error": "Chưa kết nối đến Google Sheets"}
            
            email_count = self.get_email_count()
            current_time = time.time()
            
            # Tính toán rate limit status
            time_in_window = current_time - self.write_window_start
            remaining_quota = max(0, 50 - self.write_count)
            
            return {
                "status": "connected",
                "email_count": email_count,
                "sheet_title": self.worksheet.title,
                "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
                "write_count_in_window": self.write_count,
                "remaining_quota": remaining_quota,
                "window_reset_in": max(0, 60 - time_in_window) if time_in_window < 60 else 0
            }
            
        except Exception as e:
            return {"status": "error", "email_count": 0, "error": str(e)}
    
    def is_rate_limit_safe(self, operations_needed: int = 1) -> bool:
        """Kiểm tra xem có thể thực hiện số lượng operations mà không bị rate limit"""
        current_time = time.time()
        
        # Reset counter nếu đã qua 1 phút
        if current_time - self.write_window_start >= 60:
            self.write_count = 0
            self.write_window_start = current_time
        
        return (self.write_count + operations_needed) <= 50
