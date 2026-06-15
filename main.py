from sqlalchemy import create_engine
from etl.scripts.extract.orchestrator import run_extraction
from etl.scripts.transform.orchstrator import run_reconciled_phase
from logger.logger import AppLogger
from sources import SOURCES

log = AppLogger(name="main", log_file="main.log")





log = AppLogger(name="main", log_file="etl.log")


if __name__ == "__main__":
    log.info("=== ETL START ===")

    engine = create_engine(
        "postgresql+psycopg2://postgres:Postgres123:_@localhost:5433/olist_star_schema"
    )

    try:
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
        log.info("--- PHASE: TRANSFORM / RECONCILED ---")

        reconciled_results = run_reconciled_phase(
            engine=engine,
            selected_jobs=None,
            fail_fast=True
        )

        for job_name, status in reconciled_results.items():
            log.info(f"[main] Reconciled job {job_name}: {status}")

        # ── LOAD ─────────────────────────────────────────────
        log.info("--- PHASE: LOAD ---")
        log.info("[main] DW load phase not implemented yet")

        log.info("=== ETL COMPLETE ===")

    except Exception as e:
        log.error(f"[main] ETL FAILED: {e}")
        raise