from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from datetime import datetime
import random, string, os

from app.auth import router as auth_router
from app.db import (
    get_conn,
    get_user_urls,
    add_url,
    get_original_url,
    increment_click
)
from app import config


# =========================================================
# 🔹 إعداد التطبيق
# =========================================================
app = FastAPI(
    title="نظام تقصير الروابط",
    description="خدمة آمنة لتقصير الروابط للمستخدمين المصرح لهم فقط",
    version="1.1.0"
)

# إعداد الملفات الثابتة
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# إعداد القوالب
templates = Jinja2Templates(directory="app/templates")

# تفعيل CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تضمين مسارات التحقق (الإيميل و OTP)
app.include_router(auth_router)


# =========================================================
# 🧩 استخراج المستخدم الحالي من JWT
# =========================================================
def get_current_user_email(request: Request) -> str:
    """قراءة البريد الإلكتروني من Cookie JWT"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="لم يتم تسجيل الدخول")

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="توكن غير صالح")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="انتهت صلاحية الجلسة، يرجى تسجيل الدخول مجددًا")


# =========================================================
# 🏠 الصفحات الرئيسية
# =========================================================
@app.get("/", response_class=HTMLResponse)
def home():
    """تحويل الزائر تلقائيًا إلى صفحة تسجيل الدخول"""
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """صفحة تسجيل الدخول بالبريد"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/verify", response_class=HTMLResponse)
def verify_page(request: Request, email: str = ""):
    """صفحة إدخال كود التحقق"""
    return templates.TemplateResponse("verify.html", {"request": request, "email": email})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, email: str = Depends(get_current_user_email)):
    """عرض لوحة التحكم الخاصة بالمستخدم"""
    urls = get_user_urls(email)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "email": email, "urls": urls}
    )


# =========================================================
# ✂️ إنشاء رابط مختصر
# =========================================================
@app.post("/shorten", response_class=JSONResponse)
def shorten_url(request: Request, original_url: str = Form(...), email: str = Depends(get_current_user_email)):
    """إنشاء رابط مختصر مرتبط بالبريد المسجل"""
    if not original_url.startswith(("http://", "https://")):
        original_url = "https://" + original_url  # تأمين الرابط

    short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    add_url(email=email, original_url=original_url, short_code=short_code)

    short_url = f"http://127.0.0.1:8000/{short_code}"
    return {"status": "success", "short_url": short_url}


# =========================================================
# 📋 عرض روابط المستخدم بصيغة JSON
# =========================================================
@app.get("/my-urls", response_class=JSONResponse)
def my_urls(email: str = Depends(get_current_user_email)):
    """جلب جميع روابط المستخدم بصيغة JSON"""
    urls = get_user_urls(email)
    return {"email": email, "urls": [dict(row) for row in urls]}


# =========================================================
# 🚮 حذف رابط مختصر
# =========================================================
@app.delete("/delete/{short_code}", response_class=JSONResponse)
def delete_url(short_code: str, email: str = Depends(get_current_user_email)):
    """حذف رابط معين مرتبط بالمستخدم الحالي"""
    conn = get_conn()
    cur = conn.cursor()

    # تحقق من أن الرابط يعود لنفس المستخدم
    cur.execute("SELECT email FROM urls WHERE short_code = ?", (short_code,))
    result = cur.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="الرابط غير موجود")

    owner_email = result[0]
    if owner_email != email:
        conn.close()
        raise HTTPException(status_code=403, detail="غير مصرح لك بحذف هذا الرابط")

    # تنفيذ الحذف
    cur.execute("DELETE FROM urls WHERE short_code = ?", (short_code,))
    conn.commit()
    conn.close()

    return {"status": "success", "message": "تم حذف الرابط بنجاح"}


# =========================================================
# 🔁 إعادة التوجيه للرابط الأصلي
# =========================================================
@app.get("/{short_code}")
def redirect_short_url(short_code: str):
    """إعادة توجيه المستخدم للرابط الأصلي"""
    original_url = get_original_url(short_code)

    if not original_url:
        return HTMLResponse(
            "<h1 style='text-align:center;color:red;margin-top:100px;'>❌ الرابط غير موجود</h1>",
            status_code=404
        )

    # زيادة عدد النقرات
    increment_click(short_code)

    return RedirectResponse(url=original_url)
