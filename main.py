from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

from etl.scripts.extract.orchestrator import run_staging_phase
from etl.scripts.transform.orchstrator import run_reconciled_phase
from etl.scripts.load.orchestrator import run_dw_pipeline
from logger.logger import AppLogger

log = AppLogger(name="main", log_file="main.log")


def reset_staging_and_reconciled(engine_staging, engine_reconciled) -> None:
    log.info("[main] Reset staging and reconciled started")

    with engine_staging.begin() as conn:
        conn.execute(text("""
            TRUNCATE TABLE
                staging.stg_sellers,
                staging.stg_customers,
                staging.stg_products,
                staging.stg_product_category_translation,
                staging.stg_order_payments,
                staging.stg_orders,
                staging.stg_geolocation,
                staging.stg_order_items,
                staging.stg_order_reviews,
                staging.etl_checkpoint
        """))
        log.info("[main] Staging tables truncated")

    with engine_reconciled.begin() as conn:
        conn.execute(text("""
            TRUNCATE TABLE
                reconciled.rcl_customers,
                reconciled.rcl_sellers,
                reconciled.rcl_orders,
                reconciled.rcl_order_items,
                reconciled.rcl_order_payments,
                reconciled.rcl_order_reviews,
                reconciled.rcl_products,
                reconciled.rcl_product_category_translation,
                reconciled.rcl_geolocation
        """))
        log.info("[main] Reconciled tables truncated")

    log.info("[main] Reset staging and reconciled completed")


if __name__ == "__main__":
    load_dotenv()
    log.info("=== ETL START ===")

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5433")

    staging_db = os.getenv("POSTGRES_STAGING_DB", "olist_staging")
    reconciled_db = os.getenv("POSTGRES_RECONCILED_DB", "olist_reconciled")
    dw_db = os.getenv("POSTGRES_DW_DB", "olist_dw")

    engine_staging = create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{staging_db}"
    )
    engine_reconciled = create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{reconciled_db}"
    )
    engine_dw = create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dw_db}"
    )

    log.info(f"Staging DB: {staging_db}")
    log.info(f"Reconciled DB: {reconciled_db}")
    log.info(f"DW DB: {dw_db}")

    try:
        reset_staging_and_reconciled(engine_staging, engine_reconciled)

        log.info("--- PHASE: EXTRACT / STAGING ---")
        staging_results = run_staging_phase(
            engine_write=engine_staging,
            selected_jobs=None,
            fail_fast=True,
            batch_size=5000
        )

        for job_name, status in staging_results.items():
            log.info(f"[main] Staging job {job_name}: {status}")

        log.info("--- PHASE: TRANSFORM / RECONCILED ---")
        reconciled_results = run_reconciled_phase(
            engine_read=engine_staging,
            engine_write=engine_reconciled,
            selected_jobs=None,
            fail_fast=True
        )

        for job_name, status in reconciled_results.items():
            log.info(f"[main] Reconciled job {job_name}: {status}")

        log.info("--- PHASE: LOAD / DW ---")
        run_dw_pipeline(
            engine_read=engine_reconciled,
            engine_write=engine_dw
        )

        log.info("=== ETL COMPLETE ===")

    except Exception as e:
        log.error(f"[main] ETL FAILED: {e}")
        raise