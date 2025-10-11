from app.db import init_db, get_conn

init_db()
conn = get_conn()
print("✅ قاعدة البيانات تم إنشاؤها بنجاح!")

# عرض الجداول للتأكد
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("📋 الجداول:", [t["name"] for t in tables])
conn.close()
