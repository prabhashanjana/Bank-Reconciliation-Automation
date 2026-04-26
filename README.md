# Bank Reconciliation Automation

A Python pipeline that automatically matches bank statement transactions against internal ledger entries, classifies exceptions, writes results to Google Sheets, and emails a formatted report to the auditor.

Built as a portfolio project for automation consulting — targeting audit firms and accounting practices.

---

## What It Does

| Step | Module | Output |
|------|--------|--------|
| Load CSVs | `loader.py` | Cleaned bank + ledger DataFrames |
| Validate schema | `validator.py` | Pandera-validated DataFrames |
| Categorise transactions | `categoriser.py` | Category column on each row |
| Match transactions | `matcher.py` | Matched pairs + exception list |
| Write to Google Sheets | `sheets_writer.py` | 3 tabs: Matched, Exceptions, Summary |
| Email report | `email_sender.py` | HTML report to auditor inbox |

### Matching Engine — 6 Passes

The matcher works from most confident to least confident, stopping when a match is found:

1. **Unique** — exact amount + category, unique on both sides, date ±5 days
2. **Exact** — exact amount + category + exact date
3. **Fuzzy date** — exact amount + category + date ±5 days
4. **Amount only** — rounded amount + date ±5 days
5. **Sum matching** — multiple bank rows summing to one ledger entry (e.g. 3 × LKR 50,000 → LKR 150,000)
6. **Near amount** — amount within ±5% + category + date ±5 days

Unmatched rows are classified as `BANK_ONLY` or `BOOK_ONLY` exceptions with a nearest candidate hint.

---

## Project Structure

```
bank_recon/
├── main.py                  # Entry point — runs the full pipeline
├── config.py                # File paths, column mappings, matching constants
├── .env                     # Credentials (never commit this)
├── .env.example             # Template for required environment variables
├── credentials.json         # Google service account key (never commit this)
├── data/
│   ├── bank_statement.csv   # Input: bank statement
│   └── internal_books.csv   # Input: internal ledger
├── output/                  # Local output files (optional)
├── templates/
│   └── email_report.html    # Email template (future upgrade)
└── src/
    ├── loader.py
    ├── validator.py
    ├── categoriser.py
    ├── matcher.py
    ├── sheets_writer.py
    └── email_sender.py
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/prabhashanjana/Bank-Reconciliation-Automation.git
cd Bank-Reconciliation-Automation
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `BANK_FILE` | Path to bank statement CSV |
| `LEDGER_FILE` | Path to internal ledger CSV |
| `SHEET_ID` | Google Sheets ID from the URL |
| `EMAIL_ADDRESS` | Gmail address to send from |
| `EMAIL_PASSWORD` | Gmail App Password (not your real password) |
| `TO_EMAIL` | Recipient email address |

### 5. Set up Google Sheets access

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → enable **Google Sheets API**
3. Create a **Service Account** → download `credentials.json`
4. Place `credentials.json` in the project root
5. Share your Google Sheet with the service account email (Editor access)

### 6. Prepare your CSV files

**Bank statement** (`data/bank_statement.csv`) — required columns:
```
date, description, debit, credit
```

**Internal ledger** (`data/internal_books.csv`) — required columns:
```
date, description, debit, credit
```

> Column names are configurable in `config.py` via `BANK_COLS` and `LEDGER_COLS`.

---

## Running the Pipeline

```bash
python main.py
```

### Sample output

```
INFO  | load_bank: 17 rows loaded
INFO  | load_ledger: 15 rows loaded
INFO  | validate_bank: OK — 17 rows
INFO  | validate_ledger: OK — 15 rows
INFO  | categorise: 17/17 rows categorised
INFO  | layer 0: 12 pairs matched
INFO  | layer 4: 3 bank rows → ledger L-014 sum=150000.0
INFO  | layer 5: B-011 -6750.0 ↔ L-010 -6800.0 diff=0.74%
INFO  | Matched: 16 (94.1%)
INFO  | Exceptions: 2 (BANK_ONLY: 1, BOOK_ONLY: 1)
INFO  | write_matched: 16 rows written
INFO  | write_exceptions: 2 rows written
INFO  | write_summary: 7 rows written
INFO  | send_report: email sent to auditor@firm.com
```

### Google Sheets output

The pipeline writes three tabs to your Google Sheet:

- **Matched** — all confirmed transaction pairs with match type and confidence
- **Exceptions** — unmatched rows with exception type and nearest candidate hint
- **Summary** — total rows, matched count, match rate %, exception breakdown

---

## Configuration

All constants live in `config.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `DATE_TOLERANCE_EXACT` | 0 days | Tolerance for exact date matching |
| `DATE_TOLERANCE_FUZZY` | 5 days | Tolerance for fuzzy date matching |
| `NEAR_AMOUNT_PCT` | 0.05 | Amount tolerance for near-match (5%) |
| `AMOUNT_ROUND_BASE` | 100 | Rounding base for amount-only matching |
| `CATEGORY_RULES` | list | Keyword → category mapping |

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| `pandas` | Data loading, cleaning, transformation |
| `pandera` | Schema validation with human-readable errors |
| `gspread` | Google Sheets read/write via service account |
| `smtplib` | HTML email delivery via Gmail |
| `loguru` | Structured logging with rotation |
| `python-dotenv` | Environment variable management |
| `openpyxl` | Excel file support |

---

## Roadmap

- [ ] AI-powered categorisation using Gemini API (replacing keyword rules)
- [ ] PDF bank statement extraction using pdfplumber
- [ ] Gmail attachment fetcher for automated input
- [ ] Streamlit dashboard for non-technical users

---

## Author

**Prabhashanjana** — Business Automation Consultant  
Colombo, Sri Lanka  
[GitHub](https://github.com/prabhashanjana) · [LinkedIn](https://linkedin.com/in/prabhashanjana)