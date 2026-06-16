import pandas as pd
from sqlalchemy import text

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="rcl.category_translation.load", log_file="rcl_category_translation.log")


def extract_product_category_translation_from_staging(engine) -> pd.DataFrame:
    log.info("[load_rcl_product_category_translation] Extract started")

    if engine is None:
        log.error("[load_rcl_product_category_translation] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            product_category_name,
            product_category_name_english
        FROM public.product_category_name_translation
    """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_rcl_product_category_translation] Rows extracted: {len(df)}")
        return df
    except Exception as e:
        log.error(f"[load_rcl_product_category_translation] Error during extract: {e}")
        raise ExtractDataError(f"Error extracting product_category_translation: {e}") from e


def load_rcl_product_category_translation_table(conn, df_rcl: pd.DataFrame) -> None:
    log.info("[load_rcl_product_category_translation] Load started")

    if conn is None:
        log.error("[load_rcl_product_category_translation] Database connection is None")
        raise LoadDataError("Database connection is None")

    if df_rcl is None or df_rcl.empty:
        log.error("[load_rcl_product_category_translation] dataframe is empty or None")
        raise LoadDataError("rcl_product_category_translation dataframe is empty or None")

    try:
        conn.execute(text("TRUNCATE TABLE reconciled.rcl_product_category_translation"))
        df_rcl.to_sql(
            "rcl_product_category_translation",
            con=conn,
            schema="reconciled",
            if_exists="append",
            index=False,
            method="multi"
        )
        log.info(f"[load_rcl_product_category_translation] Loaded rows: {len(df_rcl)}")
    except Exception as e:
        log.error(f"[load_rcl_product_category_translation] Error during load: {e}")
        raise LoadDataError(f"Error loading rcl_product_category_translation: {e}") from e