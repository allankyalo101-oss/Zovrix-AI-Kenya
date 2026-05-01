"""
Email and Critical Alerting Module

Purpose:
- Sends critical alerts to CloudStaff operator when orchestrator encounters failures.
- Complements WhatsApp escalation messages to client owners.

Responsibilities:
- Email notifications for exceptions and processing failures.
- Structured alert content including sender, message, error, and client_id.

Excludes:
- Sending non-critical operational logs.
- Direct interaction with clients or Twilio.
- Any message processing logic (handled by orchestrator).
"""

import smtplib
from email.message import EmailMessage
from app.config import settings

def send_alert(subject: str, message: str, recipients: list = None):
    """
    Send a critical alert via email.

    Args:
        subject (str): Alert subject line.
        message (str): Body of the alert message.
        recipients (list, optional): List of email addresses. Defaults to operator_email in settings.
    """
    if recipients is None:
        recipients = [settings.OPERATOR_EMAIL] if settings.OPERATOR_EMAIL else []

    if not recipients or not settings.SMTP_SERVER or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"[ALERTING WARNING] Cannot send email alert. Missing SMTP or operator settings. Subject: {subject}")
        print(message)
        return

    email_msg = EmailMessage()
    email_msg['Subject'] = subject
    email_msg['From'] = settings.OPERATOR_EMAIL
    email_msg['To'] = ", ".join(recipients)
    email_msg.set_content(message)

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email_msg)
    except Exception as e:
        # Logging to console only; must not block orchestrator
        print(f"[ALERTING ERROR] Failed to send alert: {repr(e)}")