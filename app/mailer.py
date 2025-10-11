import smtplib
from email.message import EmailMessage
from app import config


def send_verification_email(to_email: str, otp_code: str):
    """
    إرسال كود التحقق عبر Gmail، ويظهر المرسل كالبريد الوزاري الرسمي.
    """
    msg = EmailMessage()
    msg["Subject"] = "🔐 رمز التحقق - نظام تقصير الروابط"
    msg["From"] = f"نظام تقصير الروابط - وزارة التعليم <ashehri9348@moe.gov.sa>"
    msg["To"] = to_email

    # نص البريد HTML الرسمي
    msg.set_content(
        f"""
السلام عليكم ورحمة الله وبركاته 🌷

رمز التحقق الخاص بك هو: {otp_code}
⏱️ صالح لمدة {config.OTP_TTL_MINUTES} دقيقة فقط.

تحياتي،
نظام تقصير الروابط - وزارة التعليم
""")

    msg.add_alternative(f"""
    <html dir="rtl" lang="ar">
      <body style="font-family: 'Cairo', Tahoma, sans-serif; background-color: #f4f6f8; padding: 30px;">
        <div style="max-width:600px; margin:auto; background:#fff; border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1); overflow:hidden;">
          <div style="background-color:#0a7261; color:white; padding:16px 0; text-align:center; font-size:20px; font-weight:bold;">
            نظام تقصير الروابط - وزارة التعليم
          </div>
          <div style="padding:30px; text-align:right; color:#333;">
            <p style="font-size:18px;">مرحبًا بك 👋</p>
            <p style="font-size:16px; line-height:1.8;">
              رمز التحقق الخاص بك هو:
              <br>
              <span style="display:inline-block; background-color:#e8f5e9; color:#0a7261; padding:10px 18px; border-radius:8px; font-size:24px; font-weight:bold; letter-spacing:3px;">
                {otp_code}
              </span>
            </p>
            <p style="margin-top:20px; font-size:15px; color:#555;">
              ⏱️ الرمز صالح لمدة <b>{config.OTP_TTL_MINUTES} دقيقة فقط</b>.
            </p>
            <hr style="margin:25px 0; border:none; border-top:1px solid #eee;">
            <p style="font-size:13px; color:#777;">
              📧 أُرسل هذا البريد تلقائيًا من نظام تقصير الروابط التابع لقسم الأمن والسلامة.<br>
              يُرجى عدم الرد على هذه الرسالة.
            </p>
          </div>
          <div style="background-color:#f4f6f8; text-align:center; padding:10px; font-size:12px; color:#666;">
            وزارة التعليم - المملكة العربية السعودية
          </div>
        </div>
      </body>
    </html>
    """, subtype="html")

    try:
        with smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT) as server:
            server.starttls()
            server.login(config.EMAIL_USER, config.EMAIL_PASS)
            server.send_message(msg)
            print(f"✅ تم إرسال الرمز إلى {to_email}")
    except Exception as e:
        print(f"❌ فشل إرسال البريد: {e}")
        raise
