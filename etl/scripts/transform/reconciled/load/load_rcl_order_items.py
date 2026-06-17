import pandas as pd
from sqlalchemy import text

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="rcl.order_items.load", log_file="rcl_order_items.log")


def extract_order_items_from_staging(engine) -> pd.DataFrame:
    log.info("[load_rcl_order_items] Extract from order_items started")

    if engine is None:
        log.error("[load_rcl_order_items] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
            SELECT order_id,
                   order_item_id,
                   product_id,
                   seller_id,
                   shipping_limit_date,
                   price,
                   freight_value
            FROM staging.stg_order_items
            """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_rcl_order_items] Rows extracted: {len(df)}")
        return df
    except Exception as e:
        log.error(f"[load_rcl_order_items] Error during extract: {e}")
        raise ExtractDataError(f"Error extracting order_items: {e}") from e


def load_rcl_order_items_table(conn, df_rcl: pd.DataFrame) -> None:
    log.info("[load_rcl_order_items] Load into rcl_order_items started")

    if conn is None:
        log.error("[load_rcl_order_items] Database connection is None")
        raise LoadDataError("Database connection is None")

    if df_rcl is None or df_rcl.empty:
        log.error("[load_rcl_order_items] rcl_order_items dataframe is empty or None")
        raise LoadDataError("rcl_order_items dataframe is empty or None")

    try:
        conn.execute(text("TRUNCATE TABLE reconciled.rcl_order_items"))
        df_rcl.to_sql("rcl_order_items", con=conn, schema="reconciled", if_exists="append", index=False, method="multi")
        log.info(f"[load_rcl_order_items] Loaded rows: {len(df_rcl)}")
    except Exception as e:
        log.error(f"[load_rcl_order_items] Error during load: {e}")
        raise LoadDataError(f"Error loading rcl_order_items: {e}") from e