from sqlalchemy import create_engine

import sources
from etl.extract.orchestrator import run_extraction
import pandas as pd
from etl.trasform import transform_dim_sellers, transform_dim_customers, transform_dim_product, transform_dim_payment, \
    transform_dim_date, transform_review_info, transform_fact_table
from logger.logger import AppLogger
from sources import SOURCES
from etl.load import (
    load_dim_sellers,
    load_dim_customers,
    load_dim_product,
    load_dim_payment,
    load_dim_date,
    load_fact_table
)

log = AppLogger(name="main", log_file="main.log")



if __name__ == "__main__":
    log.info("=== ETL START ===")

    engine = create_engine(
        "postgresql+psycopg2://postgres:Postgres123:_@localhost:5433/olist_star_schema"
    )

    # ── EXTRACT ──────────────────────────────────────────
    log.info("--- PHASE: EXTRACT ---")
    with engine.connect() as conn:
        for source_name, source_config in SOURCES.items():
            log.info(f"[main] Starting extraction for {source_name}")
            run_extraction(
                conn=conn,
                csv_path=source_config["file"],
                selected_columns=source_config["columns"],
                batch_size=1000,
                target_table=source_config["staging_table"],
                truncate=False
            )
            log.info(f"[main] Extraction completed for {source_name}")




    # ── TRANSFORM ────────────────────────────────────────
    log.info("--- PHASE: TRANSFORM ---")


    # ── LOAD ─────────────────────────────────────────────
    log.info("--- PHASE: LOAD ---")


    log.info("=== ETL COMPLETE ===")