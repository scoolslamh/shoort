import os
from dotenv import load_dotenv

# تحميل القيم من ملف .env
load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

ALLOWED_DOMAINS = [d.strip().lower() for d in os.getenv("ALLOWED_DOMAINS", "").split(",") if d.strip()]

JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "6"))

OTP_TTL_MINUTES = int(os.getenv("OTP_TTL_MINUTES", "10"))
OTP_RESEND_SECONDS = int(os.getenv("OTP_RESEND_SECONDS", "60"))
OTP_MAX_TRIES = int(os.getenv("OTP_MAX_TRIES", "5"))

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
