from config import CATEGORY_RULES, AMOUNT_ROUND_BASE
from loguru import logger
from dotenv import load_dotenv
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


load_dotenv()
logger.add("app.log", rotation="1 week")


def prepare(df: pd.DataFrame, source: str) -> pd.DataFrame:

    if df.empty:
        logger.warning(f"prepare({source}): empty DataFrame — skipping")
        return df

    out = df.copy()

    out["source"] = source
    out["description_upper"] = out["description"].str.upper().str.strip()
    out["amount_rounded"] = (
        out["amount"] / AMOUNT_ROUND_BASE).round() * AMOUNT_ROUND_BASE
    out["matched"] = False
    out["match_type"] = ""
    out["confidence"] = 0

    logger.info(f"prepare({source}): {len(out)} rows ready")
    return out


def categorise(df: pd.DataFrame) -> pd.DataFrame:

    if df.empty:
        logger.warning("categorise: empty DataFrame — skipping")
        return df

    out = df.copy()
    out["category"] = "other"

    for keyword, cat in CATEGORY_RULES:
        mask = (
            out["category"].eq("other") &
            out["description_upper"].str.contains(keyword, na=False)
        )
        out.loc[mask, "category"] = cat

    n_other = out["category"].eq("other").sum()
    n_total = len(out)

    logger.info(
        f"categorise: {n_total - n_other}/{n_total} rows categorised "
        f"({n_other} still 'other')"
    )

    if n_other > 0:
        uncategorised = out.loc[
            out["category"].eq("other"), "description"
        ].tolist()
        logger.warning(f"Uncategorised: {uncategorised}")

    return out


def prepare_and_categorise(df: pd.DataFrame, source: str) -> pd.DataFrame:
    prepared = prepare(df, source)
    return categorise(prepared)
