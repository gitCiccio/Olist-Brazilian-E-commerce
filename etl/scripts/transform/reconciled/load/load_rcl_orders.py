import pandas as pd
from sqlalchemy import text

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="rcl.orders.load", log_file="rcl_orders.log")


def extract_orders_from_staging(engine) -> pd.DataFrame:
    log.info("[load_rcl_orders] Extract from orders started")

    if engine is None:
        log.error("[load_rcl_orders] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            order_id,
            customer_id,
            order_status,
            order_purchase_timestamp,
            order_approved_at,
            order_delivered_carrier_date,
            order_delivered_customer_date,
            order_estimated_delivery_date
        FROM public.orders
    """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_rcl_orders] Rows extracted: {len(df)}")
        return df
    except Exception as e:
        log.error(f"[load_rcl_orders] Error during extract: {e}")
        raise ExtractDataError(f"Error extracting orders: {e}") from e


def load_rcl_orders_table(conn, df_rcl: pd.DataFrame) -> None:
    log.info("[load_rcl_orders] Load into rcl_orders started")

    if conn is None:
        log.error("[load_rcl_orders] Database connection is None")
        raise LoadDataError("Database connection is None")

    if df_rcl is None or df_rcl.empty:
        log.error("[load_rcl_orders] rcl_orders dataframe is empty or None")
        raise LoadDataError("rcl_orders dataframe is empty or None")

    try:
        conn.execute(text("TRUNCATE TABLE reconciled.rcl_orders"))
        df_rcl.to_sql("rcl_orders", con=conn, schema="reconciled", if_exists="append", index=False, method="multi")
        log.info(f"[load_rcl_orders] Loaded rows: {len(df_rcl)}")
    except Exception as e:
        log.error(f"[load_rcl_orders] Error during load: {e}")
        raise LoadDataError(f"Error loading rcl_orders: {e}") from e