import pandas as pd
from sqlalchemy import text

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="rcl.sellers.load", log_file="rcl_sellers.log")


def extract_sellers_from_staging(engine) -> pd.DataFrame:
    log.info("[load_rcl_sellers] Extract from sellers started")

    if engine is None:
        log.error("[load_rcl_sellers] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            seller_id,
            seller_zip_code_prefix,
            seller_city,
            seller_state
        FROM public.sellers
    """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_rcl_sellers] Rows extracted: {len(df)}")
        return df
    except Exception as e:
        log.error(f"[load_rcl_sellers] Error during extract: {e}")
        raise ExtractDataError(f"Error extracting sellers: {e}") from e


def load_rcl_sellers_table(conn, df_rcl: pd.DataFrame) -> None:
    log.info("[load_rcl_sellers] Load into rcl_sellers started")

    if conn is None:
        log.error("[load_rcl_sellers] Database connection is None")
        raise LoadDataError("Database connection is None")

    if df_rcl is None or df_rcl.empty:
        log.error("[load_rcl_sellers] rcl_sellers dataframe is empty or None")
        raise LoadDataError("rcl_sellers dataframe is empty or None")

    try:
        conn.execute(text("TRUNCATE TABLE reconciled.rcl_sellers"))
        df_rcl.to_sql("rcl_sellers", con=conn, schema="reconciled", if_exists="append", index=False, method="multi")
        log.info(f"[load_rcl_sellers] Loaded rows: {len(df_rcl)}")
    except Exception as e:
        log.error(f"[load_rcl_sellers] Error during load: {e}")
        raise LoadDataError(f"Error loading rcl_sellers: {e}") from e