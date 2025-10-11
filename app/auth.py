from fastapi import APIRouter, Form, HTTPException, Response
from datetime import datetime, timedelta, timezone
import random, string
from jose import jwt

from app import config
from app.db import get_conn
from app.mailer import send_verification_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ====== أدوات مساعدة ======
def utcnow():
    """إرجاع الوقت الحالي بتوقيت UTC"""
    return datetime.now(timezone.utc)


def generate_otp():
    """توليد كود تحقق مكون من 6 أرقام"""
    return ''.join(random.choices(string.digits, k=6))


# ====== إرسال رمز التحقق ======
@router.post("/send-otp")
def send_otp(email: str = Form(...)):
    """إرسال كود تحقق إلى البريد المدخل (مع خيار السماح العام أو التقييد بالنطاق)"""
    domain = email.split("@")[-1].lower()

    # ✅ التحقق من السماح أو التقييد
    if not config.ALLOW_ALL_EMAILS and domain not in config.ALLOWED_DOMAINS:
        raise HTTPException(status_code=403, detail="❌ الدخول مسموح فقط لبريد الشركة المصرح به")

    otp = generate_otp()
    now = utcnow()
    expires_at = (now + timedelta(minutes=config.OTP_TTL_MINUTES)).isoformat()

    # حفظ الكود في قاعدة البيانات (استبدال القديم)
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM otps WHERE email=?", (email,))
    c.execute(
        "INSERT INTO otps (email, otp, expires_at) VALUES (?, ?, ?)",
        (email, otp, expires_at)
    )
    conn.commit()
    conn.close()

    # إرسال الكود عبر البريد
    send_verification_email(email, otp)

    return {"status": "success", "message": f"✅ تم إرسال رمز التحقق إلى {email}"}


# ====== التحقق من الرمز ======
@router.post("/verify-otp")
async def verify_otp(response: Response, email: str = Form(...), otp: str = Form(...)):
    """التحقق من صحة الرمز المرسل عبر البريد"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT otp, expires_at FROM otps WHERE email=?", (email,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="لم يتم العثور على رمز تحقق لهذا البريد.")

    stored_otp, expires_at = row

    # ✅ التحقق من انتهاء الصلاحية
    expires_at_dt = datetime.fromisoformat(expires_at)
    if expires_at_dt.replace(tzinfo=None) < datetime.utcnow().replace(tzinfo=None):
        conn.close()
        raise HTTPException(status_code=400, detail="⏱️ انتهت صلاحية الرمز. الرجاء طلب رمز جديد.")

    # ✅ التحقق من التطابق
    if otp != stored_otp:
        conn.close()
        raise HTTPException(status_code=401, detail="❌ رمز التحقق غير صحيح.")

    # ✅ نجاح التحقق: حذف السجل بعد الاستخدام
    cursor.execute("DELETE FROM otps WHERE email=?", (email,))
    conn.commit()
    conn.close()

    # ✅ إنشاء توكن JWT
    token = jwt.encode(
        {
            "sub": email,
            "exp": int((utcnow() + timedelta(hours=config.JWT_EXPIRES_HOURS)).timestamp())
        },
        config.JWT_SECRET,
        algorithm="HS256"
    )

    # ✅ تخزين التوكن في Cookie آمن
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite=config.COOKIE_SAMESITE,
        secure=config.COOKIE_SECURE,
        max_age=config.JWT_EXPIRES_HOURS * 3600
    )

    return {"status": "success", "message": "✅ تم التحقق بنجاح"}


# ====== تسجيل الخروج ======
@router.post("/logout")
def logout(response: Response):
    """تسجيل الخروج ومسح الكوكي"""
    response.delete_cookie("access_token")
    return {"status": "success", "message": "🚪 تم تسجيل الخروج بنجاح"}
