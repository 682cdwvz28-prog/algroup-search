import smtplib
from email.mime.text import MIMEText
from email.header import Header

SMTP_HOST = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = "you@example.com"
SMTP_PASSWORD = "PASSWORD"
FROM_EMAIL = "you@example.com"
FROM_NAME = "Алгруп"

def render_template(company: str | None = None):
    name = company or "Коллеги"
    return f"""
Здравствуйте, {name}!

Мы занимаемся поставками кабельно-проводниковой продукции и можем предложить аналоги под ваши спецификации.

Если вам актуально — пришлите, пожалуйста, номенклатуру или ТЗ, и мы подготовим предложение.

С уважением,
Алгруп
"""

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = Header(FROM_NAME, "utf-8")
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, [to_email], msg.as_string())
