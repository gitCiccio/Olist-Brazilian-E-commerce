import pandas as pd
from sqlalchemy import text

from etl.scripts.data_quality.dq_dim_seller import run_dq_dim_seller
from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError
from etl.scripts.load.build.build_dim_seller import build_dim_seller

log = AppLogger(name="dw.load_dim_seller", log_file="dw_load.log")


def extract_rcl_sellers(engine) -> pd.DataFrame:
    log.info("[load_dim_seller] Extract from rcl_sellers started")

    if engine is None:
        log.error("[load_dim_seller] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            seller_id,
            seller_city,
            seller_state,
            seller_region
        FROM reconciled.rcl_sellers
    """

    try:
        df_rcl = pd.read_sql(query, engine)
        log.info(f"[load_dim_seller] Rows extracted from rcl_sellers: {len(df_rcl)}")
        return df_rcl

    except Exception as e:
        log.error(f"[load_dim_seller] Error during extract from rcl_sellers: {e}")
        raise ExtractDataError(f"Error extracting rcl_sellers: {e}") from e


def load_dim_seller_table(conn, dim_seller: pd.DataFrame) -> None:
    log.info("[load_dim_seller] Load into dim_seller started")

    if conn is None:
        log.error("[load_dim_seller] Database connection is None")
        raise LoadDataError("Database connection is None")

    if dim_seller is None:
        log.error("[load_dim_seller] dim_seller dataframe is None")
        raise LoadDataError("dim_seller dataframe is None")

    if dim_seller.empty:
        log.error("[load_dim_seller] dim_seller dataframe is empty")
        raise LoadDataError("dim_seller dataframe is empty")

    required_cols = [
        "natural_key",
        "seller_region",
        "seller_city",
        "seller_state"
    ]
    missing = [c for c in required_cols if c not in dim_seller.columns]
    if missing:
        log.error(f"[load_dim_seller] Missing required columns in dim_seller: {missing}")
        raise LoadDataError(f"Missing required columns in dim_seller: {missing}")

    try:

        log.info(f"[load_dim_seller] Inserting rows into dim_seller: {len(dim_seller)}")
        dim_seller.to_sql(
            "dim_seller",
            con=conn,
            if_exists="append",
            index=False,
            method="multi"
        )

        log.info("[load_dim_seller] Load into dim_seller completed")

    except Exception as e:
        log.error(f"[load_dim_seller] Error during load into dim_seller: {e}")
        raise LoadDataError(f"Error loading dim_seller: {e}") from e


def run_load_dim_seller(engine, conn) -> None:
    log.info("[load_dim_seller] Pipeline started")

    df_rcl = extract_rcl_sellers(engine)
    dim_seller = build_dim_seller(df_rcl)
    load_dim_seller_table(conn, dim_seller)

    dq_path = run_dq_dim_seller(
        source_df=df_rcl,
        transformed_df=dim_seller,
        engine_dw=conn
    )

    log.info(f"[load_dim_seller] DQ report saved: {dq_path}")
    log.info("[load_dim_seller] Pipeline completed")