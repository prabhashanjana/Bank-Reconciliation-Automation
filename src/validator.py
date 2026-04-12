import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
logger.add("app.log", rotation="1 week")

BANK_SCHEMA = DataFrameSchema(
    {
        "row_id": Column(
            pa.String,
            Check.str_startswith("B-"),
            nullable=False,
        ),
        "date": Column(
            pa.DateTime,
            nullable=False,
        ),
        "debit": Column(
            pa.Float,
            Check.greater_than_or_equal_to(0),
            nullable=False,
        ),
        "credit": Column(
            pa.Float,
            Check.greater_than_or_equal_to(0),
            nullable=False,
        ),
        "amount": Column(
            pa.Float,
            nullable=False,
        ),
    },
    coerce=True,
    strict=False,
)


LEDGER_SCHEMA = DataFrameSchema(
    {
        "row_id": Column(
            pa.String,
            Check.str_startswith("L-"),
            nullable=False,
        ),
        "date": Column(
            pa.DateTime,
            nullable=False,
        ),
        "debit": Column(
            pa.Float,
            Check.greater_than_or_equal_to(0),
            nullable=False,
        ),
        "credit": Column(
            pa.Float,
            Check.greater_than_or_equal_to(0),
            nullable=False,
        ),
        "amount": Column(
            pa.Float,
            nullable=False,
        ),
    },
    coerce=True,
    strict=False,
)


def validate_bank(df: pd.DataFrame) -> pd.DataFrame:
    """Validate bank DataFrame against BANK_SCHEMA.

    Args:
        df: DataFrame to validate.

    Returns:
        Validated DataFrame or original DataFrame if validation fails.
    """
    if df.empty:
        logger.warning("validate_bank: received empty DataFrame")
        return df
    try:
        validated = BANK_SCHEMA.validate(df, lazy=True)
        logger.info(f"validate_bank: OK — {len(validated)} rows")
        return validated
    except pa.errors.SchemaErrors as e:
        logger.warning(f"validate_bank: violations:\n{e.failure_cases}")
        return df
    except Exception as e:
        logger.warning(f"validate_bank unexpected error: {e}")
        return df


def validate_ledger(df: pd.DataFrame) -> pd.DataFrame:
    """Validate ledger DataFrame against LEDGER_SCHEMA.

    Args:
        df: DataFrame to validate.

    Returns:
        Validated DataFrame or original DataFrame if validation fails.
    """
    if df.empty:
        logger.warning("validate_ledger: received empty DataFrame")
        return df
    try:
        validated = LEDGER_SCHEMA.validate(df, lazy=True)
        logger.info(f"validate_ledger: OK — {len(validated)} rows")
        return validated
    except pa.errors.SchemaErrors as e:
        logger.warning(f"validate_ledger violations:\n{e.failure_cases}")
        return df
    except Exception as e:
        logger.warning(f"validate_ledger unexpected error: {e}")
        return df


# testing...
if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.loader import load_bank, load_ledger

    bank = load_bank()
    ledger = load_ledger()

    bank_v = validate_bank(bank)
    ledger_v = validate_ledger(ledger)

    logger.info(f"Bank shape   : {bank_v.shape}")
    logger.info(f"Ledger shape : {ledger_v.shape}")
