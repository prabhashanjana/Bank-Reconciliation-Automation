import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from config import BANK_FILE, LEDGER_FILE, BANK_COLS, LEDGER_COLS
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, ".")


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def load_bank() -> pd.DataFrame:
    try:
        raw = pd.read_csv(BANK_FILE)
    except Exception as e:
        logger.warning(f"Could not read bank file: {e}")
        return pd.DataFrame()

    df = raw.copy()
    df.rename(columns=BANK_COLS, inplace=True)

    # description
    df["description"] = df["description"].fillna("").astype(str).str.strip()

    # amount
    df["debit"] = _safe_numeric(df["debit"])
    df["credit"] = _safe_numeric(df["credit"])
    df["amount"] = df["credit"] - df["debit"]

    # date column cleaning
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    n_bad = df["date"].isna().sum()
    if n_bad:
        logger.warning(f"load_bank: {n_bad} unparseable dates → NaT")

    # add row_ID colomn
    df.insert(0, "row_id", [f"B-{i+1:03d}" for i in range(len(df))])

    logger.info(f"load_bank: {len(df)} rows loaded")
    return df[["row_id", "date", "description", "debit", "credit", "amount"]]


def load_ledger() -> pd.DataFrame:
    try:
        raw = pd.read_csv(LEDGER_FILE)
    except Exception as e:
        logger.warning(f"Could not read ledger file: {e}")
        return pd.DataFrame()

    df = raw.copy()
    df.rename(columns=LEDGER_COLS, inplace=True)

    # description
    df["description"] = df["description"].fillna("").astype(str).str.strip()

    # amount
    df["debit"] = _safe_numeric(df["debit"])
    df["credit"] = _safe_numeric(df["credit"])
    df["amount"] = df["credit"] - df["debit"]

    # date column cleaning
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    n_bad = df["date"].isna().sum()
    if n_bad:
        logger.warning(f"load_ledger {n_bad} unparseable dates → NaT")

    # add row_ID colomn
    df.insert(0, "row_id", [f"L-{i+1:03d}" for i in range(len(df))])

    logger.info(f"load_ledger: {len(df)} rows loaded")
    return df[["row_id", "date", "description", "debit", "credit", "amount"]]
