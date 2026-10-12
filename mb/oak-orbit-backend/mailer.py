"""Order email sender. Real SMTP if configured via env vars, otherwise saves
.eml files to outbox/ so the flow works out of the box."""
import os, ssl, smtplib, time, re
from email.message import EmailMessage
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
OUTBOX = Path(BASE_DIR) / "outbox"
OUTBOX.mkdir(exist_ok=True)

SMTP_HOST = os.environ.get("SMTP_HOST", "")        # e.g. smtp.gmail.com
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER or "no-reply@oakorbit.com")


def _deliver(msg):
    if SMTP_HOST:
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.starttls(context=ssl.create_default_context())
                if SMTP_USER:
                    s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
            return "sent via SMTP"
        except Exception as e:
            print(f"[mailer] SMTP failed ({e}); falling back to outbox")
    fname = OUTBOX / f"{int(time.time()*1000)}.eml"
    fname.write_text(msg.as_string(), encoding="utf-8")
    return f"saved to outbox/{fname.name} (set SMTP_HOST/SMTP_USER/SMTP_PASS to send real email)"


def send_order_confirmation(to_email, order):
    lines = "\n".join(
        f"  - {l['n']}  x{l['q']}  ${l['p'] * l['q']:.2f}" for l in order["lines"]
    )
    body = f"""Hi {order['address']['name']},

Thanks for your order from Oak & Orbit! 

Order number : {order['id']}
Status       : {order['status']}

Items:
{lines}

Subtotal : ${order['subtotal']:.2f}
Discount : -${order['discount']:.2f}
Shipping : ${order['shipping']:.2f}
TOTAL    : ${order['total']:.2f}

Shipping to:
  {order['address']['address']}, {order['address']['city']} {order['address']['zip']}

We will email you again when your order ships.
— Oak & Orbit support (support@oakorbit.com)
"""
    msg = EmailMessage()
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = f"Order confirmed: {order['id']} — Oak & Orbit"
    msg.set_content(body)
    result = _deliver(msg)
    print(f"[mailer] order {order['id']} -> {to_email}: {result}")