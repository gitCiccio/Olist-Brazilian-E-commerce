from typing import Callable, Dict, List, Optional
import os

from logger.logger import AppLogger
from sqlalchemy import create_engine
from dotenv import load_dotenv
from typing import Callable, Dict, List, Optional

# job runner is implemented locally in this module

# Reconciled build/extract/load functions (explicit imports so orchestrator can run)
from etl.scripts.transform.reconciled.load.load_rcl_customers import extract_customers_from_staging, load_rcl_customers_table
from etl.scripts.transform.reconciled.build.build_rcl_customers import build_rcl_customers

from etl.scripts.transform.reconciled.load.load_rcl_sellers import extract_sellers_from_staging, load_rcl_sellers_table
from etl.scripts.transform.reconciled.build.build_rcl_sellers import build_rcl_sellers

from etl.scripts.transform.reconciled.load.load_rcl_orders import extract_orders_from_staging, load_rcl_orders_table
from etl.scripts.transform.reconciled.build.build_rcl_orders import build_rcl_orders

from etl.scripts.transform.reconciled.load.load_rcl_order_items import extract_order_items_from_staging, load_rcl_order_items_table
from etl.scripts.transform.reconciled.build.build_rcl_order_items import build_rcl_order_items

from etl.scripts.transform.reconciled.load.load_rcl_order_payments import extract_order_payments_from_staging, load_rcl_order_payments_table
from etl.scripts.transform.reconciled.build.build_rcl_order_payments import build_rcl_order_payments

from etl.scripts.transform.reconciled.load.load_rcl_order_reviews import extract_order_reviews_from_staging, load_rcl_order_reviews_table
from etl.scripts.transform.reconciled.build.build_rcl_order_reviews import build_rcl_order_reviews

from etl.scripts.transform.reconciled.load.load_rcl_products import extract_products_from_staging, load_rcl_products_table
from etl.scripts.transform.reconciled.build.build_rcl_products import build_rcl_products

from etl.scripts.transform.reconciled.load.load_rcl_product_category_translation import extract_product_category_translation_from_staging, load_rcl_product_category_translation_table
from etl.scripts.transform.reconciled.build.build_rcl_product_category_translation import build_rcl_product_category_translation

from etl.scripts.transform.reconciled.load.load_rcl_geolocation import extract_geolocation_from_staging, load_rcl_geolocation_table
from etl.scripts.transform.reconciled.build.build_rcl_geolocation import build_rcl_geolocation

log = AppLogger(name="reconciled.orchestrator", log_file="reconciled_phase.log")



def _run_single_reconciled_job(
    engine,
    job_name: str,
    extract_fn: Callable,
    build_fn: Callable,
    load_fn: Callable,
) -> int:
    log.info(f"[reconciled.orchestrator] Starting job: {job_name}")

    if engine is None:
        log.error(f"[reconciled.orchestrator] Engine is None for job: {job_name}")
        raise RuntimeError(f"Database engine is None for job: {job_name}")

    df_source = extract_fn(engine)
    source_rows = len(df_source)
    log.info(f"[reconciled.orchestrator] {job_name} extracted rows: {source_rows}")

    df_rcl = build_fn(df_source)
    reconciled_rows = len(df_rcl)
    log.info(f"[reconciled.orchestrator] {job_name} reconciled rows: {reconciled_rows}")

    with engine.begin() as conn:
        load_fn(conn, df_rcl)

    log.info(f"[reconciled.orchestrator] Completed job: {job_name}")
    return reconciled_rows


def run_reconciled_phase(
    engine,
    selected_jobs: Optional[List[str]] = None,
    fail_fast: bool = True,
) -> Dict[str, str]:
    log.info(
        f"[reconciled.orchestrator] Reconciled phase started "
        f"(selected_jobs={selected_jobs}, fail_fast={fail_fast})"
    )


    if engine is None:
        log.error("[reconciled.orchestrator] get_engine returned None")
        raise RuntimeError("Database engine is None")

    jobs = {
        "customers": (
            extract_customers_from_staging,
            build_rcl_customers,
            load_rcl_customers_table,
        ),
        "sellers": (
            extract_sellers_from_staging,
            build_rcl_sellers,
            load_rcl_sellers_table,
        ),
        "orders": (
            extract_orders_from_staging,
            build_rcl_orders,
            load_rcl_orders_table,
        ),
        "order_items": (
            extract_order_items_from_staging,
            build_rcl_order_items,
            load_rcl_order_items_table,
        ),
        "order_payments": (
            extract_order_payments_from_staging,
            build_rcl_order_payments,
            load_rcl_order_payments_table,
        ),
        "order_reviews": (
            extract_order_reviews_from_staging,
            build_rcl_order_reviews,
            load_rcl_order_reviews_table,
        ),
        "products": (
            extract_products_from_staging,
            build_rcl_products,
            load_rcl_products_table,
        ),
        "product_category_translation": (
            extract_product_category_translation_from_staging,
            build_rcl_product_category_translation,
            load_rcl_product_category_translation_table,
        ),
        "geolocation": (
            extract_geolocation_from_staging,
            build_rcl_geolocation,
            load_rcl_geolocation_table,
        ),
    }

    execution_order = [
        "customers",
        "sellers",
        "orders",
        "order_items",
        "order_payments",
        "order_reviews",
        "products",
        "product_category_translation",
        "geolocation",
    ]

    if selected_jobs:
        unknown_jobs = [job for job in selected_jobs if job not in jobs]
        if unknown_jobs:
            log.error(f"[reconciled.orchestrator] Unknown jobs requested: {unknown_jobs}")
            raise ValueError(f"Unknown jobs requested: {unknown_jobs}")

        execution_order = [job for job in execution_order if job in selected_jobs]

    results: Dict[str, str] = {}

    for job_name in execution_order:
        extract_fn, build_fn, load_fn = jobs[job_name]

        try:
            loaded_rows = _run_single_reconciled_job(
                engine=engine,
                job_name=job_name,
                extract_fn=extract_fn,
                build_fn=build_fn,
                load_fn=load_fn,
            )
            results[job_name] = f"SUCCESS ({loaded_rows} rows)"

        except Exception as e:
            log.error(f"[reconciled.orchestrator] Job failed: {job_name} -> {e}")
            results[job_name] = f"FAILED ({e})"

            if fail_fast:
                log.error("[reconciled.orchestrator] Reconciled phase interrupted due to fail_fast=True")
                raise

    log.info(f"[reconciled.orchestrator] Reconciled phase completed with results: {results}")
    return results

