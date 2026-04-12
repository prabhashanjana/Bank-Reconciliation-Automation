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


if __name__ == "__main__":
    logger.add("app.log", rotation="1 week")
    logger.info("Starting test suite")

    bank, ledger = test_loader()
    bank_v, ledger_v = test_validator(bank, ledger)

    logger.info("=" * 50)
    logger.info("ALL TESTS PASSED")
    logger.info("=" * 50)
