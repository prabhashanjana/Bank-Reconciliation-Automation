from config import CONFIDENCE, DATE_TOLERANCE_FUZZY, DATE_TOLERANCE_EXACT, NEAR_AMOUNT_PCT
from loguru import logger
from dotenv import load_dotenv
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


load_dotenv()
logger.add("app.log", rotation="1 week")


def _unmatched(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["matched"].eq(False)].copy()


def _find_nearest(row: pd.Series, other_df: pd.DataFrame) -> str:
    """
    Finds the nearest unmatched row in other_df by amount + date.
    Returns a human readable hint string.
    Used for exception nearest candidate suggestions.
    """
    if other_df.empty:
        return "No candidates found"

    window_days = pd.Timedelta(days=30)
    date_min = row["date"] - window_days
    date_max = row["date"] + window_days

    nearby = other_df[
        (other_df["date"] >= date_min) &
        (other_df["date"] <= date_max)
    ].copy()

    if nearby.empty:
        return "No candidates within 30 days"

    nearby["amount_diff"] = (nearby["amount"] - row["amount"]).abs()
    best = nearby.loc[nearby["amount_diff"].idxmin()]

    return (
        f"{best['row_id']} | "
        f"{best['date'].strftime('%b %d')} | "
        f"{best['description'][:40]} | "
        f"LKR {best['amount']:,.0f}"
    )


def run_matcher(bank: pd.DataFrame, ledger: pd.DataFrame) -> tuple:
    """
    Runs all matching layeres against bank and ledger DataFrames.
    Both must already be prepared and categorised by categoriser.py

    Returns:
        matched_df    : pd.DataFrame
        exceptions_df : pd.DataFrame
        summary       : dict
    """

    logger.info("Starting matching engine")
    logger.info(f"Bank rows   : {len(bank)}")
    logger.info(f"Ledger rows : {len(ledger)}")

    b = bank.copy()
    l = ledger.copy()

    matched_pairs = []

    # matching layer 01
    # ── layer 0 ── unique amount + category + date ±5 days ──────────────
    logger.info("layer 0: unique amount + category")

    b_un = _unmatched(b)
    l_un = _unmatched(l)

    p0 = pd.merge(
        b_un, l_un,
        on=["amount", "category"],
        suffixes=("_b", "_l")
    )

    if not p0.empty:
        p0["date_diff"] = (p0["date_b"] - p0["date_l"]).abs()
        p0 = p0[p0["date_diff"] <= DATE_TOLERANCE_FUZZY]

    if not p0.empty:
        b_counts = p0.groupby("row_id_b")["row_id_l"].count()
        l_counts = p0.groupby("row_id_l")["row_id_b"].count()
        unique_b = b_counts[b_counts == 1].index
        unique_l = l_counts[l_counts == 1].index
        p0 = p0[
            p0["row_id_b"].isin(unique_b) &
            p0["row_id_l"].isin(unique_l)
        ]

    for _, row in p0.iterrows():
        matched_pairs.append({
            "bank_row_id": row["row_id_b"],
            "ledger_row_id": row["row_id_l"],
            "bank_amount": row["amount"],
            "ledger_amount": row["amount"],
            "date": row["date_b"],
            "description": row["description_b"],
            "match_type": "unique",
            "confidence": CONFIDENCE["exact"],
        })
        b.loc[b["row_id"].eq(row["row_id_b"]), "matched"] = True
        l.loc[l["row_id"].eq(row["row_id_l"]), "matched"] = True

    logger.info(f"layer 0: {len(p0)} pairs matched")

    # matching layer 02
    # ── layer 1 ── exact amount + category + exact date ─────────────────
    logger.info("layer 1: exact amount + category + exact date")

    b_un = _unmatched(b)
    l_un = _unmatched(l)

    p1 = pd.merge(
        b_un, l_un,
        on=["amount", "category"],
        suffixes=("_b", "_l")
    )

    if not p1.empty:
        p1["date_diff"] = (p1["date_b"] - p1["date_l"]).abs()
        p1 = p1[p1["date_diff"] <= DATE_TOLERANCE_EXACT]

    for _, row in p1.iterrows():
        matched_pairs.append({
            "bank_row_id": row["row_id_b"],
            "ledger_row_id": row["row_id_l"],
            "bank_amount": row["amount"],
            "ledger_amount": row["amount"],
            "date": row["date_b"],
            "description": row["description_b"],
            "match_type": "exact",
            "confidence": CONFIDENCE["exact"],
        })
        b.loc[b["row_id"].eq(row["row_id_b"]), "matched"] = True
        l.loc[l["row_id"].eq(row["row_id_l"]), "matched"] = True

    logger.info(f"layer 1: {len(p1)} pairs matched")

    # matching layer 02
    # ── layer 02 ── exact amount + category + fuzzy date ±5 days ────────
    logger.info("layer 02: exact amount + category + fuzzy date")

    b_un = _unmatched(b)
    l_un = _unmatched(l)

    p2 = pd.merge(
        b_un, l_un,
        on=["amount", "category"],
        suffixes=("_b", "_l")
    )

    if not p2.empty:
        p2["date_diff"] = (p2["date_b"] - p2["date_l"]).abs()
        p2 = p2[p2["date_diff"] <= DATE_TOLERANCE_FUZZY]

    for _, row in p2.iterrows():
        matched_pairs.append({
            "bank_row_id": row["row_id_b"],
            "ledger_row_id": row["row_id_l"],
            "bank_amount": row["amount"],
            "ledger_amount": row["amount"],
            "date": row["date_b"],
            "description": row["description_b"],
            "match_type": "fuzzy_date",
            "confidence": CONFIDENCE["fuzzy_date"],
        })
        b.loc[b["row_id"].eq(row["row_id_b"]), "matched"] = True
        l.loc[l["row_id"].eq(row["row_id_l"]), "matched"] = True

    logger.info(f"layer 02: {len(p2)} pairs matched")

    # matching layer 04
    # ── layer 3 ── amount only + fuzzy date ─────────────────────────────
    logger.info("layer 3: amount only + fuzzy date")

    b_un = _unmatched(b)
    l_un = _unmatched(l)

    p3 = pd.merge(
        b_un, l_un,
        on=["amount_rounded"],
        suffixes=("_b", "_l")
    )

    if not p3.empty:
        p3["date_diff"] = (p3["date_b"] - p3["date_l"]).abs()
        p3 = p3[p3["date_diff"] <= DATE_TOLERANCE_FUZZY]

    for _, row in p3.iterrows():
        matched_pairs.append({
            "bank_row_id": row["row_id_b"],
            "ledger_row_id": row["row_id_l"],
            "bank_amount": row["amount_b"],
            "ledger_amount": row["amount_l"],
            "date": row["date_b"],
            "description": row["description_b"],
            "match_type": "amount_only",
            "confidence": CONFIDENCE["amount_only"],
        })
        b.loc[b["row_id"].eq(row["row_id_b"]), "matched"] = True
        l.loc[l["row_id"].eq(row["row_id_l"]), "matched"] = True

    logger.info(f"layer 3: {len(p3)} pairs matched")

    # ── layer 4 ── sum matching + date ±5 days ──────────────────────────
    logger.info("layer 4: sum matching")

    b_un = _unmatched(b)
    l_un = _unmatched(l)

    for _, l_row in l_un.iterrows():
        date_min = l_row["date"] - DATE_TOLERANCE_FUZZY
        date_max = l_row["date"] + DATE_TOLERANCE_FUZZY

        window = b_un[
            (b_un["date"] >= date_min) &
            (b_un["date"] <= date_max) &
            (b_un["matched"].eq(False))
        ]

        if window.empty:
            continue

        if round(window["amount"].sum(), 2) == round(l_row["amount"], 2):
            for _, b_row in window.iterrows():
                matched_pairs.append({
                    "bank_row_id": b_row["row_id"],
                    "ledger_row_id": l_row["row_id"],
                    "bank_amount": b_row["amount"],
                    "ledger_amount": l_row["amount"],
                    "date": b_row["date"],
                    "description": b_row["description"],
                    "match_type": "sum_match",
                    "confidence": CONFIDENCE["sum_match"],
                })
                b.loc[b["row_id"].eq(b_row["row_id"]), "matched"] = True

            l.loc[l["row_id"].eq(l_row["row_id"]), "matched"] = True
            logger.info(
                f"layer 4: {len(window)} bank rows → "
                f"ledger {l_row['row_id']} "
                f"sum={l_row['amount']}"
            )

        # ── layer 5 ── near amount ±5% + category + fuzzy date ──────────────
    logger.info("layer 5: near amount ±5%")

    b_un = _unmatched(b)
    l_un = _unmatched(l)

    for _, b_row in b_un.iterrows():
        date_min = b_row["date"] - DATE_TOLERANCE_FUZZY
        date_max = b_row["date"] + DATE_TOLERANCE_FUZZY

        # find ledger rows — same category, within date window
        candidates = l_un[
            (l_un["category"].eq(b_row["category"])) &
            (l_un["date"] >= date_min) &
            (l_un["date"] <= date_max) &
            (l_un["matched"].eq(False))
        ]

        if candidates.empty:
            continue

        # check amount within 5%
        candidates = candidates.copy()
        candidates["amount_diff_pct"] = (
            (candidates["amount"] - b_row["amount"]).abs() /
            candidates["amount"].abs()
        )
        candidates = candidates[
            candidates["amount_diff_pct"] <= NEAR_AMOUNT_PCT
        ]

        if candidates.empty:
            continue

        # take closest amount match
        best = candidates.loc[candidates["amount_diff_pct"].idxmin()]

        matched_pairs.append({
            "bank_row_id": b_row["row_id"],
            "ledger_row_id": best["row_id"],
            "bank_amount": b_row["amount"],
            "ledger_amount": best["amount"],
            "date": b_row["date"],
            "description": b_row["description"],
            "match_type": "near_amount",
            "confidence": CONFIDENCE["near_amount"],
        })
        b.loc[b["row_id"].eq(b_row["row_id"]), "matched"] = True
        l.loc[l["row_id"].eq(best["row_id"]),  "matched"] = True

        logger.info(
            f"layer 5: {b_row['row_id']} {b_row['amount']} ↔ "
            f"{best['row_id']} {best['amount']} "
            f"diff={round(best['amount_diff_pct']*100, 2)}%"
        )

    # ── Exceptions ──────────────────────────────────────────────────────
    logger.info("Classifying exceptions")

    b_remaining = _unmatched(b)
    l_remaining = _unmatched(l)

    exceptions = []

    # BANK_ONLY — rows in bank with no ledger match
    for _, row in b_remaining.iterrows():
        hint = _find_nearest(row, l_remaining)
        exceptions.append({
            "exception_id": f"EX-{len(exceptions)+1:03d}",
            "type": "BANK_ONLY",
            "date": row["date"],
            "description": row["description"],
            "bank_amount": row["amount"],
            "ledger_amount": None,
            "difference": None,
            "nearest_candidate": hint,
        })

    # BOOK_ONLY — rows in ledger with no bank match
    for _, row in l_remaining.iterrows():
        hint = _find_nearest(row, b_remaining)
        exceptions.append({
            "exception_id": f"EX-{len(exceptions)+1:03d}",
            "type": "BOOK_ONLY",
            "date": row["date"],
            "description": row["description"],
            "bank_amount": None,
            "ledger_amount": row["amount"],
            "difference": None,
            "nearest_candidate": hint,
        })

    exceptions_df = pd.DataFrame(exceptions)
    logger.info(f"Exceptions: {len(exceptions_df)} total")
    logger.info(f"  BANK_ONLY : {len(b_remaining)}")
    logger.info(f"  BOOK_ONLY : {len(l_remaining)}")

    # ── Summary ─────────────────────────────────────────────────────────
    matched_df = pd.DataFrame(matched_pairs)

    total_bank = len(bank)
    total_ledger = len(ledger)
    matched_count = len(
        matched_df["bank_row_id"].unique()) if not matched_df.empty else 0
    match_rate = round(matched_count / total_bank *
                       100, 1) if total_bank else 0

    summary = {
        "total_bank": total_bank,
        "total_ledger": total_ledger,
        "matched": matched_count,
        "match_rate_pct": match_rate,
        "exceptions": len(exceptions_df),
        "bank_only": len(b_remaining),
        "book_only": len(l_remaining),
    }

    logger.info("=" * 50)
    logger.info(f"Total bank        : {total_bank}")
    logger.info(f"Total ledger      : {total_ledger}")
    logger.info(f"Matched           : {matched_count} ({match_rate}%)")
    logger.info(f"Exceptions        : {len(exceptions_df)}")
    logger.info(f"  BANK_ONLY       : {len(b_remaining)}")
    logger.info(f"  BOOK_ONLY       : {len(l_remaining)}")
    logger.info("=" * 50)

    return matched_df, exceptions_df, summary
