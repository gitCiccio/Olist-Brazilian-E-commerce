import pandas as pd
from sqlalchemy import text

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="rcl.geolocation.load", log_file="rcl_geolocation.log")


def extract_geolocation_from_staging(engine) -> pd.DataFrame:
    log.info("[load_rcl_geolocation] Extract from geolocation started")

    if engine is None:
        log.error("[load_rcl_geolocation] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            geolocation_zip_code_prefix,
            geolocation_lat,
            geolocation_lng,
            geolocation_city,
            geolocation_state
        FROM staging.stg_geolocation
    """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_rcl_geolocation] Rows extracted: {len(df)}")
        return df
    except Exception as e:
        log.error(f"[load_rcl_geolocation] Error during extract: {e}")
        raise ExtractDataError(f"Error extracting geolocation: {e}") from e


def load_rcl_geolocation_table(conn, df_rcl: pd.DataFrame) -> None:
    log.info("[load_rcl_geolocation] Load into rcl_geolocation started")

    if conn is None:
        log.error("[load_rcl_geolocation] Database connection is None")
        raise LoadDataError("Database connection is None")

    if df_rcl is None or df_rcl.empty:
        log.error("[load_rcl_geolocation] dataframe is empty or None")
        raise LoadDataError("rcl_geolocation dataframe is empty or None")

    try:
        conn.execute(text("TRUNCATE TABLE reconciled.rcl_geolocation"))
        df_rcl.to_sql("rcl_geolocation", con=conn, schema="reconciled", if_exists="append", index=False, method="multi")
        log.info(f"[load_rcl_geolocation] Loaded rows: {len(df_rcl)}")
    except Exception as e:
        log.error(f"[load_rcl_geolocation] Error during load: {e}")
        raise LoadDataError(f"Error loading rcl_geolocation: {e}") from e