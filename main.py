from sqlalchemy import create_engine

from etl.extract import extract_and_stage
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
    df_sellers   = extract_and_stage(SOURCES['dim_seller']['file'],   SOURCES['dim_seller']['columns'],   'stg_sellers',        engine, truncate=True)
    df_customers = extract_and_stage(SOURCES['dim_customer']['file'], SOURCES['dim_customer']['columns'], 'stg_customers',      engine, truncate=True)
    df_products  = extract_and_stage(SOURCES['dim_product']['file'],  SOURCES['dim_product']['columns'],  'stg_products',       engine, truncate=True)
    df_payments  = extract_and_stage(SOURCES['dim_payment']['file'],  SOURCES['dim_payment']['columns'],  'stg_order_payments', engine, truncate=True)
    df_orders    = extract_and_stage(SOURCES['dim_date']['file'],    SOURCES['dim_date']['columns'],    'stg_orders',         engine, truncate=True)
    df_items     = extract_and_stage(SOURCES['order_items_info']['file'], SOURCES['order_items_info']['columns'], 'stg_order_items', engine, truncate=True)
    df_reviews   = extract_and_stage(SOURCES['review_info']['file'],    SOURCES['review_info']['columns'],    'stg_order_reviews',  engine, truncate=True)


    # ── TRANSFORM ────────────────────────────────────────
    log.info("--- PHASE: TRANSFORM ---")
    df_dim_sellers   = transform_dim_sellers(df_sellers)
    df_dim_customers = transform_dim_customers(df_customers)
    df_dim_products  = transform_dim_product(df_products)

    df_dim_payment, df_payment_type_lookup, df_payment_value_lookup = transform_dim_payment(df_payments)
    df_dim_date, order_fact_lookup = transform_dim_date(df_orders)
    df_review_lookup                                                 = transform_review_info(df_reviews)

    df_fact = transform_fact_table(
        df_items,
        order_fact_lookup,
        df_payment_type_lookup,
        df_payment_value_lookup,
        df_review_lookup
    )

    # ── LOAD ─────────────────────────────────────────────
    log.info("--- PHASE: LOAD ---")
    load_dim_sellers(df_dim_sellers, engine)

    log.info("--- PHASE LOAD: SELLERS ENDED ---")
    load_dim_customers(df_dim_customers, engine)

    log.info("--- PHASE LOAD: CUSTOMERS ENDED ---")
    load_dim_product(df_dim_products, engine)

    log.info("--- PHASE LOAD: PRODUCT ENDED ---")
    load_dim_payment(df_dim_payment, engine)

    log.info("--- PHASE LOAD: PAYMENT ENDED ---")
    _, date_mapping = load_dim_date(df_dim_date, engine)

    log.info("--- PHASE LOAD: DATE ENDED ---")
    load_fact_table(df_fact, date_mapping, engine)

    log.info("--- PHASE LOAD: FACT TABLE ENDED ---")

    log.info("=== ETL COMPLETE ===")