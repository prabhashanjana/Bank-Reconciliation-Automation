from src.validator import validate_bank, validate_ledger
from src.loader import load_bank, load_ledger
from loguru import logger
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


def test_loader():
    logger.info("=" * 50)
    logger.info("TEST: loader.py")
    logger.info("=" * 50)

    bank = load_bank()
    ledger = load_ledger()

    logger.info(f"\n=== Bank ===\n{bank.to_string()}")
    logger.info(f"\n=== Ledger ===\n{ledger.to_string()}")
    logger.info(f"Bank shape   : {bank.shape}")
    logger.info(f"Ledger shape : {ledger.shape}")

    assert bank.shape == (17, 6), f"Expected (17,6) got {bank.shape}"
    assert ledger.shape == (15, 6), f"Expected (15,6) got {ledger.shape}"

    logger.info("test_loader: PASSED")
    return bank, ledger


def test_validator(bank, ledger):
    logger.info("=" * 50)
    logger.info("TEST: validator.py")
    logger.info("=" * 50)

    bank_v = validate_bank(bank)
    ledger_v = validate_ledger(ledger)

    logger.info(f"Bank validated shape   : {bank_v.shape}")
    logger.info(f"Ledger validated shape : {ledger_v.shape}")

    assert not bank_v.empty,   "Bank validation returned empty DataFrame"
    assert not ledger_v.empty, "Ledger validation returned empty DataFrame"

    logger.info("test_validator: PASSED")
    return bank_v, ledger_v


def test_categoriser(bank_v, ledger_v):
    logger.info("=" * 50)
    logger.info("TEST: categoriser.py")
    logger.info("=" * 50)

    from src.categoriser import prepare_and_categorise

    bank_c = prepare_and_categorise(bank_v,   "bank")
    ledger_c = prepare_and_categorise(ledger_v, "ledger")

    cols = ["row_id", "description", "amount", "category"]
    logger.info(f"\n=== Bank categories ===\n{bank_c[cols].to_string()}")
    logger.info(f"\n=== Ledger categories ===\n{ledger_c[cols].to_string()}")

    # all rows must have a source tag
    assert bank_c["source"].eq("bank").all(),     "Bank source tag wrong"
    assert ledger_c["source"].eq("ledger").all(), "Ledger source tag wrong"

    # matched must start False
    assert not bank_c["matched"].any(),   "Bank matched must start False"
    assert not ledger_c["matched"].any(), "Ledger matched must start False"

    # no row should be uncategorised in our sample data
    bank_other = bank_c["category"].eq("other").sum()
    ledger_other = ledger_c["category"].eq("other").sum()
    if bank_other > 0:
        logger.warning(
            f"Bank has {bank_other} uncategorised rows — add rules to config.py")
    if ledger_other > 0:
        logger.warning(
            f"Ledger has {ledger_other} uncategorised rows — add rules to config.py")

    # shared categories check
    bank_cats = set(bank_c["category"].unique())
    ledger_cats = set(ledger_c["category"].unique())
    shared = bank_cats & ledger_cats
    logger.info(f"Shared categories : {sorted(shared)}")
    logger.info(f"Bank only         : {sorted(bank_cats - ledger_cats)}")
    logger.info(f"Ledger only       : {sorted(ledger_cats - bank_cats)}")

    logger.info("test_categoriser: PASSED ✓")
    return bank_c, ledger_c


if __name__ == "__main__":
    logger.add("app.log", rotation="1 week")
    logger.info("Starting test suite")

    try:
        bank, ledger = test_loader()
        bank_v, ledger_v = test_validator(bank, ledger)
        bank_c, ledger_c = test_categoriser(bank_v, ledger_v)

        logger.info("=" * 50)
        logger.info("ALL TESTS PASSED ✓")
        logger.info("=" * 50)

    except AssertionError as e:
        logger.error(f"TEST FAILED: {e}")
    except Exception as e:
        logger.error(f"UNEXPECTED ERROR: {e}")
