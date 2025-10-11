import sqlite3
import os
from datetime import datetime

# مسار قاعدة البيانات
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")


def get_conn():
    """فتح اتصال آمن بقاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # تسهيل الوصول إلى الأعمدة بالاسم
    return conn


def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول إذا لم تكن موجودة"""
    conn = get_conn()
    c = conn.cursor()

    # ✅ جدول الرموز (OTP)
    c.execute("""
        CREATE TABLE IF NOT EXISTS otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            otp TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)

    # ✅ جدول الروابط (URLs)
    c.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            original_url TEXT NOT NULL,
            short_code TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            clicks INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    print("✅ قاعدة البيانات تم إنشاؤها أو تحديثها بنجاح!")


def add_url(email: str, original_url: str, short_code: str):
    """إضافة رابط جديد مع ربطه بالبريد الإلكتروني"""
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO urls (email, original_url, short_code, created_at) VALUES (?, ?, ?, ?)",
        (email, original_url, short_code, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_user_urls(email: str):
    """جلب جميع الروابط الخاصة بمستخدم معين"""
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, original_url, short_code, created_at, clicks FROM urls WHERE email=? ORDER BY id DESC",
        (email,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


def increment_click(short_code: str):
    """زيادة عدد النقرات عند استخدام الرابط"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,))
    conn.commit()
    conn.close()


def get_original_url(short_code: str):
    """جلب الرابط الأصلي من الكود المختصر"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_code=?", (short_code,))
    row = c.fetchone()
    conn.close()
    return row["original_url"] if row else None


# عند التشغيل المباشر (اختبار فقط)
if __name__ == "__main__":
    init_db()
