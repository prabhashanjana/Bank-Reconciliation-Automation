from pathlib import Path

import pandas as pd
from loguru import logger

logger.add("app.log", rotation="1 week")

try:
    Path("data").mkdir(exist_ok=True)
    logger.info("data/ directory ready")
except Exception as e:
    logger.warning(f"Could not create data/ directory: {e}")


bank_data = {
    "Transaction Date": [
        # exact matches
        "01/03/2025",   # Silva rent
        "03/03/2025",   # Dialog
        "05/03/2025",   # Perera — ledger Mar 06 (date offset)
        "07/03/2025",   # Keells
        "10/03/2025",   # Fernando
        "12/03/2025",   # ATM
        "14/03/2025",   # Sampath charge — bank only
        "15/03/2025",   # Jayawardena
        "18/03/2025",   # SLT
        "20/03/2025",   # Silva Mar
        "22/03/2025",   # CEB — amount mismatch
        "25/03/2025",   # Bandara — ledger Mar 26 (date offset)
        "27/03/2025",   # Arpico — ledger Mar 29 (date offset)
        "28/03/2025",   # Gunawardena
        # one-to-many — 3 deposits sum to LKR 150,000
        "08/03/2025",   # Ranasinghe part 1
        "09/03/2025",   # Ranasinghe part 2
        "10/03/2025",   # Ranasinghe part 3
    ],
    "Narration": [
        "IBFT CR TRF FM 0094512 SILVA",
        "DIALOG AXIATA PLC DD",
        "IBFT DR TRF TO 0078234 PERERA",
        "POS PURCHASE KEELLS SUPER NUGEGODA",
        "IBFT CR TRF FM 0031892 FERNANDO",
        "ATM WITHDRAWAL NUGEGODA BR",
        "SAMPATH BANK SERVICE CHARGE",
        "IBFT DR TRF TO 0056123 JAYAWARDENA",
        "SLT MOBITEL DD",
        "IBFT CR TRF FM 0094512 SILVA",
        "LANKA ELECTRICITY BOARD DD",
        "IBFT DR TRF TO 0099341 BANDARA",
        "POS PURCHASE ARPICO BATTARAMULLA",
        "IBFT CR TRF FM 0044781 GUNAWARDENA",
        "IBFT CR TRF FM 0071234 RANASINGHE",
        "IBFT CR TRF FM 0071234 RANASINGHE",
        "IBFT CR TRF FM 0071234 RANASINGHE",
    ],
    "Debit(LKR)": [
        None, 2850.00, 15000.00, 4320.00, None,
        20000.00, 500.00, 8500.00, 1200.00, None,
        6750.00, 30000.00, 12400.00, None,
        None, None, None,
    ],
    "Credit(LKR)": [
        45000.00, None, None, None, 120000.00,
        None, None, None, None, 45000.00,
        None, None, None, 18000.00,
        50000.00, 50000.00, 50000.00,
    ],
    "Balance(LKR)": [
        125000.00, 122150.00, 107150.00, 102830.00, 222830.00,
        202830.00, 202330.00, 193830.00, 192630.00, 237630.00,
        230880.00, 200880.00, 188480.00, 206480.00,
        256480.00, 306480.00, 356480.00,
    ],
}


bank_data = {
    "Transaction Date": [
        # exact matches
        "01/03/2025",   # Silva rent
        "03/03/2025",   # Dialog
        "05/03/2025",   # Perera — ledger Mar 06 (date offset)
        "07/03/2025",   # Keells
        "10/03/2025",   # Fernando
        "12/03/2025",   # ATM
        "14/03/2025",   # Sampath charge — bank only
        "15/03/2025",   # Jayawardena
        "18/03/2025",   # SLT
        "20/03/2025",   # Silva Mar
        "22/03/2025",   # CEB — amount mismatch
        "25/03/2025",   # Bandara — ledger Mar 26 (date offset)
        "27/03/2025",   # Arpico — ledger Mar 29 (date offset)
        "28/03/2025",   # Gunawardena
        # one-to-many — 3 deposits sum to LKR 150,000
        "08/03/2025",   # Ranasinghe part 1
        "09/03/2025",   # Ranasinghe part 2
        "10/03/2025",   # Ranasinghe part 3
    ],
    "Narration": [
        "IBFT CR TRF FM 0094512 SILVA",
        "DIALOG AXIATA PLC DD",
        "IBFT DR TRF TO 0078234 PERERA",
        "POS PURCHASE KEELLS SUPER NUGEGODA",
        "IBFT CR TRF FM 0031892 FERNANDO",
        "ATM WITHDRAWAL NUGEGODA BR",
        "SAMPATH BANK SERVICE CHARGE",
        "IBFT DR TRF TO 0056123 JAYAWARDENA",
        "SLT MOBITEL DD",
        "IBFT CR TRF FM 0094512 SILVA",
        "LANKA ELECTRICITY BOARD DD",
        "IBFT DR TRF TO 0099341 BANDARA",
        "POS PURCHASE ARPICO BATTARAMULLA",
        "IBFT CR TRF FM 0044781 GUNAWARDENA",
        "IBFT CR TRF FM 0071234 RANASINGHE",
        "IBFT CR TRF FM 0071234 RANASINGHE",
        "IBFT CR TRF FM 0071234 RANASINGHE",
    ],
    "Debit(LKR)": [
        None, 2850.00, 15000.00, 4320.00, None,
        20000.00, 500.00, 8500.00, 1200.00, None,
        6750.00, 30000.00, 12400.00, None,
        None, None, None,
    ],
    "Credit(LKR)": [
        45000.00, None, None, None, 120000.00,
        None, None, None, None, 45000.00,
        None, None, None, 18000.00,
        50000.00, 50000.00, 50000.00,
    ],
    "Balance(LKR)": [
        125000.00, 122150.00, 107150.00, 102830.00, 222830.00,
        202830.00, 202330.00, 193830.00, 192630.00, 237630.00,
        230880.00, 200880.00, 188480.00, 206480.00,
        256480.00, 306480.00, 356480.00,
    ],
}

ledger_data = {
    "Date": [
        # exact matches
        "02/03/2025",   # Silva — bank Mar 01 (date offset)
        "03/03/2025",   # Dialog
        "06/03/2025",   # Perera — bank Mar 05 (date offset)
        "07/03/2025",   # Keells
        "10/03/2025",   # Fernando
        "12/03/2025",   # Petty cash
        "15/03/2025",   # Jayawardena
        "18/03/2025",   # SLT
        "20/03/2025",   # Silva Mar
        "22/03/2025",   # CEB — amount mismatch
        "26/03/2025",   # Bandara — bank Mar 25 (date offset)
        "28/03/2025",   # Gunawardena
        "29/03/2025",   # Arpico — bank Mar 27 (date offset)
        # one-to-many — single entry = sum of 3 bank deposits
        "08/03/2025",   # Ranasinghe LKR 150,000
        # book only — cheque issued, not cleared in bank
        "31/03/2025",
    ],
    "Particulars": [
        "Rent received - Mr. Silva (Feb)",
        "Dialog mobile bill payment",
        "Staff advance - Perera",
        "Grocery purchase - Keells",
        "Commission received - Fernando deal",
        "Cash withdrawal for petty cash",
        "Loan repayment - Jayawardena",
        "SLT broadband monthly",
        "Rent received - Mr. Silva (Mar)",
        "CEB electricity bill",
        "Supplier payment - Bandara Traders",
        "Consultation fee - Gunawardena",
        "Arpico - stationery and office items",
        "Project payment - Ranasinghe Constructions",
        "CHQ 004892 ISSUED - pending clearance",
    ],
    "DR": [
        None, 2850.00, 15000.00, 4320.00, None,
        20000.00, 8500.00, 1200.00, None,
        6800.00, 30000.00, None, 12400.00,
        None,
        75000.00,
    ],
    "CR": [
        45000.00, None, None, None, 120000.00,
        None, None, None, 45000.00,
        None, None, 18000.00, None,
        150000.00,
        None,
    ],
    "Remarks": [
        "Monthly office rent",
        "March bill",
        "Personal advance",
        "Office supplies",
        "Athurugiriya land sale",
        "Office petty cash",
        "March installment",
        "Office internet",
        "Monthly office rent",
        "March electricity",
        "Invoice BT-2025-089",
        "Property valuation",
        "Quarterly stationery",
        "Invoice RC-2025-014",
        "Uncleared cheque",
    ],
}


try:
    pd.DataFrame(bank_data).to_csv("data/bank_statement.csv", index=False)
    logger.info("Bank statement written → data/bank_statement.csv")
except Exception as e:
    logger.warning(f"Failed to write bank_statement.csv: {e}")

try:
    pd.DataFrame(ledger_data).to_csv("data/internal_books.csv", index=False)
    logger.info("Ledger written → data/internal_books.csv")
except Exception as e:
    logger.warning(f"Failed to write internal_books.csv: {e}")

logger.info(f"Bank rows  : {len(bank_data['Transaction Date'])}")
logger.info(f"Ledger rows: {len(ledger_data['Date'])}")
logger.info("Expected exceptions after matching:")
logger.info("  1. BANK ONLY  — Sampath service charge LKR 500 (Mar 14)")
logger.info("  2. BOOK ONLY  — Uncleared cheque LKR 75,000 (Mar 31)")
logger.info("  3. MISMATCH   — CEB LKR 6,750 bank vs LKR 6,800 ledger")
logger.info("One-to-many — Ranasinghe 3 x LKR 50,000 = LKR 150,000 ledger")
