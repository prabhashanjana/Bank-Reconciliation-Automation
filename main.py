import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from loguru import logger

from loader import load_bank, load_ledger
from validator import validate_bank, validate_ledger
from categoriser import prepare_and_categorise
from matcher import run_matcher
from sheets_writer import run_sheets_writer
from email_sender import send_report

load_dotenv()
logger.add("app.log", rotation="1 week")


def main():
    logger.info("=" * 50)
    logger.info("Bank Reconciliation — starting")
    logger.info("=" * 50)

    # Step 1 — Load
    bank_df = load_bank()
    ledger_df = load_ledger()

    # Step 2 — Validate
    bank_df = validate_bank(bank_df)
    ledger_df = validate_ledger(ledger_df)

    # Step 3 — Prepare and categorise
    bank_df = prepare_and_categorise(bank_df, "bank")
    ledger_df = prepare_and_categorise(ledger_df, "ledger")

    # Step 4 — Match
    matched_df, exceptions_df, summary = run_matcher(bank_df, ledger_df)

    # Step 5 — Write to Google Sheets
    run_sheets_writer(matched_df, exceptions_df, summary)

    # Step 6 — Send email report
    send_report(summary, exceptions_df)

    logger.info("=" * 50)
    logger.info("Bank Reconciliation — complete")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()