from config import SHEET_ID
from loguru import logger
from dotenv import load_dotenv
import gspread
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


load_dotenv()
logger.add("app.log", rotation="1 week")


def _connect():
    """
    Authenticates with Google Sheets using credentials.json.
    Returns a gspread client.
    """
    try:
        gc = gspread.service_account(filename="credentials.json")
        logger.info("Google Sheets: connected")
        return gc
    except Exception as e:
        logger.warning(f"Google Sheets: connection failed — {e}")
        return None


def get_or_create_worksheet(spreadsheet, name):
    try:
        ws = spreadsheet.worksheet(name)        # get tab by name
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(
            title=name,                          # tab name
            rows=1000,
            cols=20
        )
    return ws


def write_matched(gc, matched_df):
    if matched_df.empty:
        logger.warning("write_matched: empty DataFrame — skipping")
        return

    try:
        spreadsheet = gc.open_by_key(SHEET_ID)
        ws = get_or_create_worksheet(spreadsheet, "Matched")
        ws.clear()

        df = matched_df.copy()
        # convert dates to string
        df["date"] = df['date'].dt.strftime('%Y-%m-%d')

        header = df.columns.tolist()                         # list of column names
        rows = df.values.tolist()                            # list of lists (the data)

        ws.update([header] + rows)
        logger.info(f"write_matched: {len(df)} rows written")

    except Exception as e:
        logger.warning(f"write_matched failed — {e}")


def write_exceptions(gc, exceptions_df):
    if exceptions_df.empty:
        logger.warning("write_exception: empty DataFrame — skipping")
        return

    try:
        spreadsheet = gc.open_by_key(SHEET_ID)
        ws = get_or_create_worksheet(spreadsheet, "Exceptions")
        ws.clear()

        df = exceptions_df.copy()
        # convert dates to string
        df["date"] = df['date'].dt.strftime('%Y-%m-%d')

        header = df.columns.tolist()                         # list of column names
        rows = df.values.tolist()                            # list of lists (the data)

        ws.update([header] + rows)
        logger.info(f"write_exceptions: {len(df)} rows written")

    except Exception as e:
        logger.warning(f"write_exceptions failed — {e}")


def write_summary(gc, summary):
    if not summary:
        logger.warning("write_summary: empty dict — skipping")
        return

    try:
        spreadsheet = gc.open_by_key(SHEET_ID)
        ws = get_or_create_worksheet(spreadsheet, "Summary")
        ws.clear()

        rows = [[k, v] for k, v in summary.items()]

        ws.update([["Metric", "Value"]] + rows)
        logger.info(f"write_summary: {len(rows)} rows written")

    except Exception as e:
        logger.warning(f"write_summary failed — {e}")


def run_sheets_writer(matched_df, exceptions_df, summary):
    gc = _connect()
    if gc is None:
        logger.warning("run_sheets_writer: no connection — skipping")
        return
    write_matched(gc, matched_df)
    write_exceptions(gc, exceptions_df)
    write_summary(gc, summary)
