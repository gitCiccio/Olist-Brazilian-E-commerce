from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from etl.scripts.load.orchestrator import run_dw_pipeline
from etl.scripts.transform.orchstrator import run_reconciled_phase
from logger.logger import AppLogger

log = AppLogger(name="main", log_file="main.log")

if __name__ == "__main__":
    load_dotenv()
    log.info("=== ETL START ===")

    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5433')

    staging_db = os.getenv('POSTGRES_STAGING_DB', 'olist_staging')
    reconciled_db = os.getenv('POSTGRES_RECONCILED_DB', 'olist_reconciled')
    dw_db = os.getenv('POSTGRES_DW_DB', 'olist_dw')

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
        log.info("--- PHASE: EXTRACT ---")
        log.info("[main] Extract phase not active (use scripts/recreate_and_load_db.py)")

        log.info("--- PHASE: TRANSFORM / RECONCILED ---")
        reconciled_results = run_reconciled_phase(
            engine_read=engine_staging,
            engine_write=engine_reconciled,
            selected_jobs=None,
            fail_fast=True
        )

        for job_name, status in reconciled_results.items():
            log.info(f"[main] Reconciled job {job_name}: {status}")

        log.info("--- PHASE: LOAD ---")
        run_dw_pipeline(
            engine_read=engine_reconciled,
            engine_write=engine_dw
        )

        log.info("=== ETL COMPLETE ===")

    except Exception as e:
        log.error(f"[main] ETL FAILED: {e}")
        raise