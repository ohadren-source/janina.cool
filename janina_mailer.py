"""
janina_mailer.py — Email delivery for janina.cool submissions
==============================================================
Sends form submissions to 36nife@gmail.com via Gmail SMTP.
In janina's register. Clipped. Cool. ✌🏿

Environment variables:
  - GMAIL_SENDER_ADDRESS: The Gmail address that sends (e.g., 36nife@gmail.com or a dedicated sender)
  - GMAIL_APP_PASSWORD:   Gmail App Password (NOT the account password — generate at
                          https://myaccount.google.com/apppasswords)
  - JANINA_INBOX:         Destination address. Defaults to 36nife@gmail.com.
  - JANINA_MAIL_ENABLED:  'true' or 'false'. If 'false' or unset and creds missing,
                          the module logs and skips rather than crashing.

If the env vars are missing, send_submission_email() returns False and logs a warning,
but does NOT raise. Janina's form still stores to the db. She is not going to fall apart
because the mailer had a bad day. Shrug.
"""

import os
import ssl
import smtplib
import logging
from email.message import EmailMessage
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 465  # SSL

DEFAULT_INBOX = '36nife@gmail.com'


def _get_config():
    """Return (sender, app_password, inbox, enabled) or (None, None, None, False) if disabled."""
    sender = os.getenv('GMAIL_SENDER_ADDRESS', '').strip()
    app_password = os.getenv('GMAIL_APP_PASSWORD', '').strip()
    inbox = os.getenv('JANINA_INBOX', DEFAULT_INBOX).strip() or DEFAULT_INBOX
    enabled_flag = os.getenv('JANINA_MAIL_ENABLED', '').strip().lower()

    # If explicitly disabled, stop here
    if enabled_flag == 'false':
        return (None, None, None, False)

    # If creds missing, can't send — disable gracefully
    if not sender or not app_password:
        return (None, None, None, False)

    return (sender, app_password, inbox, True)


# ─────────────────────────────────────────────────────────────────────────
# Message composition (janina voice)
# ─────────────────────────────────────────────────────────────────────────

def _compose_subject(submission: dict) -> str:
    """
    Subject line in janina register.
    Keep it short. Tell you what it is. No drama.
    """
    who = submission.get('name', '').strip() or submission.get('email', '').strip()
    topic = submission.get('subject', '').strip()
    if topic:
        return f"[janina.cool] {who}: {topic}"
    return f"[janina.cool] {who} said somethin"


def _compose_body(submission: dict) -> str:
    """
    Email body in janina voice. Clipped. Informational. Closes with ✌🏿.
    """
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

    name = submission.get('name', '').strip() or '(no name)'
    email = submission.get('email', '').strip() or '(no email)'
    subject = submission.get('subject', '').strip() or '(no subject)'
    message = submission.get('message', '').strip() or '(no message, they just showed up)'
    ip = submission.get('ip_address', '').strip() or '(unknown)'
    ua = submission.get('user_agent', '').strip() or '(unknown)'

    body = f"""Somebody submitted the suggestion box form. 

FROM: {name} <{email}>
SUBJECT: {subject}
WHEN: {now}

MESSAGE:
---
{message}
---

(meta: ip {ip} · ua {ua[:120]})

Filed in the db. Not openin it. You deal.

Janina
aHuman Resource
the sauc-e team
✌🏿
"""
    return body


# ─────────────────────────────────────────────────────────────────────────
# Send
# ─────────────────────────────────────────────────────────────────────────

def send_submission_email(submission: dict) -> bool:
    """
    Send an email to 36nife@gmail.com with the submission content.
    
    Args:
        submission: dict with keys email, name, subject, message,
                    ip_address, user_agent
    
    Returns:
        True if sent, False if skipped or failed. Never raises.
    """
    sender, app_password, inbox, enabled = _get_config()

    if not enabled:
        logger.info("Janina mailer disabled or creds missing — skipping email send.")
        return False

    try:
        msg = EmailMessage()
        msg['From'] = sender
        msg['To'] = inbox
        msg['Subject'] = _compose_subject(submission)

        # Reply-To header points to the submitter so Chef can reply directly
        submitter_email = submission.get('email', '').strip()
        if submitter_email:
            msg['Reply-To'] = submitter_email

        msg.set_content(_compose_body(submission))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=30) as server:
            server.login(sender, app_password)
            server.send_message(msg)

        logger.info(f"janina.cool submission emailed to {inbox}")
        return True

    except Exception as e:
        # Never raise — the db store has already happened and the user
        # should not see a 500 because an email leg failed.
        logger.error(f"Failed to send janina.cool submission email: {e}")
        return False
