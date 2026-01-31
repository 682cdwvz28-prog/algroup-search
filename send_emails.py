import os
import smtplib
from email.mime.text import MIMEText
from typing import List


SMTP_HOST = algroup.gate.sendsay.ru("SMTP_HOST")
SMTP_PORT = 587("SMTP_PORT", "587"))
SMTP_USER = algroup.algroup@smtpgate("SMTP_USER")
SMTP_PASSWORD = imi1Xoopiliyabi("SMTP_PASSWORD")
SMTP_FROM = info@promage.ru("SMTP_FROM", SMTP_USER)


def send_emails_smtp(recipients: List[str], subject: str, body: str):
    if not recipients:
        return

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, recipients, msg.as_string())
