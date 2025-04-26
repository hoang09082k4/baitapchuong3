import os
import shutil
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')

DATABASE_FOLDER = '.'
BACKUP_FOLDER = './backup/'

os.makedirs(BACKUP_FOLDER, exist_ok=True)

def send_email(subject, body):
    """Hàm gửi email."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Lỗi khi gửi mail: {e}")

def backup_database():
    """Hàm backup database."""
    try:
        files = os.listdir(DATABASE_FOLDER)
        db_files = [f for f in files if f.endswith('.sql') or f.endswith('.sqlite3')]

        if not db_files:
            send_email('Backup thất bại', 'Không tìm thấy file .sql hoặc .sqlite3 để backup.')
            return

        for file_name in db_files:
            src_path = os.path.join(DATABASE_FOLDER, file_name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file_name = f"{os.path.splitext(file_name)[0]}_{timestamp}{os.path.splitext(file_name)[1]}"
            dest_path = os.path.join(BACKUP_FOLDER, backup_file_name)

            shutil.copy2(src_path, dest_path)

        send_email('Backup thành công', f"Đã backup {len(db_files)} file database thành công.")
    except Exception as e:
        send_email('Backup thất bại', f"Đã xảy ra lỗi khi backup: {e}")

def main():
    """Hàm main chạy schedule."""
    schedule.every().day.at("00:00").do(backup_database)

    print("Đang chạy backup scheduler... Nhấn Ctrl+C để dừng.")
    while True:
        schedule.run_pending()
        time.sleep(60)  

if __name__ == '__main__':
    main()
