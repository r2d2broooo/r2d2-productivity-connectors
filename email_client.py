"""SMTP email sending for the AI models. ACTION - requires user confirmation
before being used (see desktop_tools.ACTION_TOOLS / system prompts).

Reads credentials from environment variables (set in telegram-bots/.env):
  SMTP_HOST      e.g. smtp.gmail.com
  SMTP_PORT      e.g. 465 (SSL)
  SMTP_USER      the sending account's address
  SMTP_PASSWORD  app password for that account
  SMTP_FROM      optional, defaults to SMTP_USER
"""

import asyncio
import os
import smtplib
from email.message import EmailMessage


def _send_sync(to: str, subject: str, body: str) -> str:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "465"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    sender = os.environ.get("SMTP_FROM", user)

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL(host, port) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)

    return f"Email sent to {to}."


async def send_email(to: str, subject: str, body: str) -> str:
    return await asyncio.to_thread(_send_sync, to, subject, body)
