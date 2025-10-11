import os
from dotenv import load_dotenv

# تحميل ملف .env من المسار الصحيح
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

# ====== إعدادات البريد ======
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# ====== النطاقات المسموح بها ======
ALLOWED_DOMAINS = [d.strip() for d in os.getenv("ALLOWED_DOMAINS", "").split(",") if d.strip()]

# ====== إعدادات OTP ======
OTP_TTL_MINUTES = int(os.getenv("OTP_TTL_MINUTES", 5))
OTP_MAX_TRIES = int(os.getenv("OTP_MAX_TRIES", 3))

# ====== إعدادات التوكن وملفات تعريف الارتباط ======
JWT_SECRET = os.getenv("JWT_SECRET", "your_super_secret_jwt_key_here")  # سرّ التشفير
JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", 12))  # مدة صلاحية التوكن بالساعات

# إعدادات الكوكي (تستخدم عند تسجيل الدخول)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "Lax")
# السماح لجميع الإيميلات (لتعطيل التقييد)
ALLOW_ALL_EMAILS = os.getenv("ALLOW_ALL_EMAILS", "false").lower() == "true"
