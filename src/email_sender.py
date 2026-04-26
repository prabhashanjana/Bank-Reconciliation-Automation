import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from loguru import logger
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()
logger.add("app.log", rotation="1 week")


def _build_html(summary, exceptions_df):

    summary_rows = ""
    for k, v in summary.items():
        summary_rows += f"<tr><td>{k}</td><td>{v}</td></tr>"

    if not exceptions_df.empty:
        exceptions_html = exceptions_df.to_html(
            index=False,
            columns=["exception_id", "type", "date",
                     "description", "bank_amount", "ledger_amount"]
        )
    else:
        exceptions_html = "<p>No exceptions found.</p>"

    return f"""
    <h2>Bank Reconciliation Report</h2>
    <h3>Summary</h3>
    <table border="1">{summary_rows}</table>
    <h3>Exceptions</h3>
    {exceptions_html}
    """


def send_report(summary, exceptions_df):

    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    to_email = os.getenv("TO_EMAIL")

    if not all([email_address, email_password, to_email]):
        logger.warning("send_report: missing email credentials in .env — skipping")
        return

    try:
        html = _build_html(summary, exceptions_df)

        msg = MIMEMultipart("mixed")
        msg["Subject"] = "Bank Reconciliation Report"
        msg["From"] = email_address
        msg["To"] = to_email

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, to_email, msg.as_string())

        logger.info(f"send_report: email sent to {to_email}")

    except Exception as e:
        logger.warning(f"send_report failed — {e}")