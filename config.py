from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
logger.add("app.log", rotation="1 week")

BANK_FILE = Path("data/bank_statement.csv")
LEDGER_FILE = Path("data/internal_books.csv")
OUTPUT_DIR = Path("output/")


SHEET_ID = os.getenv("SHEET_ID")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

_REQUIRED = {
    "SHEET_ID": SHEET_ID,
    "EMAIL_SENDER": EMAIL_SENDER,
    "EMAIL_PASSWORD": EMAIL_PASSWORD,
    "EMAIL_RECIPIENT": EMAIL_RECIPIENT,
}

_missing = [k for k, v in _REQUIRED.items() if not v]
if _missing:
    logger.warning(f"Missing .env keys: {_missing}")

DATE_TOLERANCE = pd.Timedelta(days=5)
AMOUNT_ROUND_BASE = 50
NEAR_AMOUNT_PCT = 0.05

CONFIDENCE = {
    "exact": 100,
    "fuzzy_date": 85,
    "amount_only": 65,
    "sum_match": 55,
    "near_amount": 50,
}


BANK_COLS = {
    "Transaction Date": "date",
    "Narration": "description",
    "Debit(LKR)": "debit",
    "Credit(LKR)": "credit",
    "Balance(LKR)": "balance",
}

LEDGER_COLS = {
    "Date": "date",
    "Particulars": "description",
    "DR": "debit",
    "CR": "credit",
    "Remarks": "reference",
}


CATEGORY_RULES: list[tuple[str, str]] = [
    ("SILVA",          "rent"),
    ("JAYAWARDENA",    "rent"),
    ("DIALOG",         "telecom"),
    ("CEB",            "utilities"),
    ("ELECTRICITY",    "utilities"),
    ("SLT",            "utilities"),
    ("MOBITEL",        "utilities"),
    ("KEELLS",         "groceries"),
    ("ARPICO",         "office_supplies"),
    ("SERVICE CHARGE", "bank_fee"),
    ("ATM",            "cash_withdrawal"),
    ("PETTY CASH",     "cash_withdrawal"),
    ("FERNANDO",       "commission"),
    ("GUNAWARDENA",    "fee_income"),
    ("RANASINGHE",     "project_payment"),
    ("BANDARA",        "supplier_payment"),
    ("CHQ",            "cheque"),
    ("CHEQUE",         "cheque"),
]
