import pandas as pd
from sqlalchemy import text

from etl.scripts.data_quality.dq_dim_customer import run_dq_dim_customer
from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError
from etl.scripts.load.build.build_dim_customer import build_dim_customer

log = AppLogger(name="dw.load_dim_customer", log_file="dw_load.log")


def extract_rcl_customers(engine) -> pd.DataFrame:
    log.info("[load_dim_customer] Extract from rcl_customers started")

    if engine is None:
        log.error("[load_dim_customer] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            customer_unique_id,
            customer_city,
            customer_state,
            customer_region
        FROM rcl_customers
    """

    try:
        df_rcl = pd.read_sql(query, engine)
        log.info(f"[load_dim_customer] Rows extracted from rcl_customers: {len(df_rcl)}")
        return df_rcl

    except Exception as e:
        log.error(f"[load_dim_customer] Error during extract from rcl_customers: {e}")
        raise ExtractDataError(f"Error extracting rcl_customers: {e}") from e


def load_dim_customer_table(conn, dim_customer: pd.DataFrame) -> None:
    log.info("[load_dim_customer] Load into dim_customer started")

    if conn is None:
        log.error("[load_dim_customer] Database connection is None")
        raise LoadDataError("Database connection is None")

    if dim_customer is None:
        log.error("[load_dim_customer] dim_customer dataframe is None")
        raise LoadDataError("dim_customer dataframe is None")

    if dim_customer.empty:
        log.error("[load_dim_customer] dim_customer dataframe is empty")
        raise LoadDataError("dim_customer dataframe is empty")

    required_cols = [
        "natural_key",
        "customer_region",
        "customer_city",
        "customer_state"
    ]
    missing = [c for c in required_cols if c not in dim_customer.columns]
    if missing:
        log.error(f"[load_dim_customer] Missing required columns in dim_customer: {missing}")
        raise LoadDataError(f"Missing required columns in dim_customer: {missing}")

    try:
        log.info("[load_dim_customer] Truncating dim_customer")
        conn.execute(text("TRUNCATE TABLE dim_customer"))

        log.info(f"[load_dim_customer] Inserting rows into dim_customer: {len(dim_customer)}")
        dim_customer.to_sql(
            "dim_customer",
            con=conn,
            if_exists="append",
            index=False,
            method="multi"
        )

        log.info("[load_dim_customer] Load into dim_customer completed")

    except Exception as e:
        log.error(f"[load_dim_customer] Error during load into dim_customer: {e}")
        raise LoadDataError(f"Error loading dim_customer: {e}") from e


def run_load_dim_customer(engine, conn) -> None:
    log.info("[load_dim_customer] Pipeline started")

    df_rcl = extract_rcl_customers(engine)
    dim_customer = build_dim_customer(df_rcl)
    load_dim_customer_table(conn, dim_customer)

    dq_path = run_dq_dim_customer(
        source_df=df_rcl,
        transformed_df=dim_customer,
        engine_dw=conn
    )
    log.info(f"[load_dim_customer] DQ report saved: {dq_path}")

    log.info("[load_dim_customer] Pipeline completed")