from app.db import init_db, get_conn

# إنشاء الجداول إذا لم تكن موجودة
init_db()

# التحقق من أن كل شيء يعمل
conn = get_conn()
print("✅ قاعدة البيانات تم إنشاؤها بنجاح!")

# عرض الجداول
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("📋 الجداول:", [t["name"] for t in tables])
conn.close()
