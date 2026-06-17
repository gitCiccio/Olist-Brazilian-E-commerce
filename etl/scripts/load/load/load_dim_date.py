import pandas as pd
from sqlalchemy import text

from etl.scripts.data_quality.dq_dim_date import run_dq_dim_date
from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError
from etl.scripts.load.build.build_dim_date import build_dim_date

log = AppLogger(name="dw.load_dim_date", log_file="dw_load.log")


def extract_date_sources(engine) -> pd.DataFrame:
    log.info("[load_dim_date] Extract date sources started")

    if engine is None:
        log.error("[load_dim_date] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT CAST(order_purchase_timestamp AS DATE) AS full_date
        FROM reconciled.rcl_orders

        UNION

        SELECT CAST(order_delivered_customer_date AS DATE) AS full_date
        FROM reconciled.rcl_orders

        UNION

        SELECT CAST(order_estimated_delivery_date AS DATE) AS full_date
        FROM  reconciled.rcl_orders

        UNION

        SELECT CAST(shipping_limit_date AS DATE) AS full_date
        FROM reconciled.rcl_order_items
    """

    try:
        df_dates = pd.read_sql(query, engine)
        log.info(f"[load_dim_date] Rows extracted for dim_date build: {len(df_dates)}")
        return df_dates

    except Exception as e:
        log.error(f"[load_dim_date] Error during extract of date sources: {e}")
        raise ExtractDataError(f"Error extracting date sources: {e}") from e


def load_dim_date_table(conn, dim_date: pd.DataFrame) -> None:
    log.info("[load_dim_date] Load into dim_date started")

    if conn is None:
        log.error("[load_dim_date] Database connection is None")
        raise LoadDataError("Database connection is None")

    if dim_date is None:
        log.error("[load_dim_date] dim_date dataframe is None")
        raise LoadDataError("dim_date dataframe is None")

    if dim_date.empty:
        log.error("[load_dim_date] dim_date dataframe is empty")
        raise LoadDataError("dim_date dataframe is empty")

    required_cols = [
        "natural_key",
        "full_date",
        "day",
        "month",
        "quarter",
        "year",
        "day_of_week",
        "week_of_year",
        "is_weekend"
    ]

    missing = [c for c in required_cols if c not in dim_date.columns]
    if missing:
        log.error(f"[load_dim_date] Missing required columns in dim_date: {missing}")
        raise LoadDataError(f"Missing required columns in dim_date: {missing}")

    try:
        log.info(f"[load_dim_date] Inserting rows into dim_date: {len(dim_date)}")
        dim_date.to_sql(
            "dim_date",
            con=conn,
            if_exists="append",
            index=False,
            method="multi"
        )

        log.info("[load_dim_date] Load into dim_date completed")

    except Exception as e:
        log.error(f"[load_dim_date] Error during load into dim_date: {e}")
        raise LoadDataError(f"Error loading dim_date: {e}") from e


def run_load_dim_date(engine, conn) -> None:
    log.info("[load_dim_date] Pipeline started")

    df_dates = extract_date_sources(engine)
    dim_date = build_dim_date(df_dates)
    load_dim_date_table(conn, dim_date)

    dq_path = run_dq_dim_date(
        source_df=df_dates,
        transformed_df=dim_date,
        engine_dw=conn
    )
    log.info(f"[load_dim_date] DQ report saved: {dq_path}")

    log.info("[load_dim_date] Pipeline completed")