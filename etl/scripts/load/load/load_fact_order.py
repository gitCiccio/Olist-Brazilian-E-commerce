import pandas as pd
from etl.scripts.data_quality.dq_fact_order import run_dq_fact_order
from etl.scripts.load.build.build_fact_order import build_fact_order
from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="dw.load_fact_order", log_file="dw_load.log")


def extract_fact_order_source(engine) -> pd.DataFrame:
    log.info("[load_fact_order] Extract started")

    if engine is None:
        log.error("[load_fact_order] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        WITH payment_agg AS (
            SELECT
                order_id,
                payment_type,
                payment_installments,
                SUM(payment_value) AS payment_value
            FROM reconciled.rcl_order_payments
            GROUP BY order_id, payment_type, payment_installments
        ),
        review_agg AS (
            SELECT
                order_id,
                ROUND(AVG(review_score)::numeric, 1) AS review_score
            FROM reconciled.rcl_order_reviews
            GROUP BY order_id
        )
        SELECT
            o.order_id,
            o.order_status,
            c.customer_unique_id AS customer_natural_key,
            p.payment_type,
            p.payment_installments,
            p.payment_value,
            r.review_score,
            CAST(o.order_purchase_timestamp AS DATE) AS purchase_date,
            CAST(o.order_delivered_customer_date AS DATE) AS delivered_date,
            CAST(o.order_estimated_delivery_date AS DATE) AS estimated_delivery_date
        FROM reconciled.rcl_orders o
        JOIN reconciled.rcl_customers c
            ON o.customer_id = c.customer_id
        LEFT JOIN payment_agg p
            ON o.order_id = p.order_id
        LEFT JOIN review_agg r
            ON o.order_id = r.order_id
    """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_fact_order] Rows extracted: {len(df)}")
        return df
    except Exception as e:
        log.error(f"[load_fact_order] Extract error: {e}")
        raise ExtractDataError(f"Error extracting fact_order source: {e}") from e


def extract_dim_maps(conn):
    customer_map = pd.read_sql(
        """
        SELECT natural_key, surrogate_key
        FROM public.dim_customer
        WHERE is_current = TRUE
        """,
        conn
    ).rename(columns={"natural_key": "customer_natural_key", "surrogate_key": "customer_key"})

    payment_map = pd.read_sql(
        """
        SELECT surrogate_key AS payment_key, payment_type, payment_installments
        FROM public.dim_payment
        """,
        conn
    )

    date_map = pd.read_sql(
        """
        SELECT surrogate_key, full_date
        FROM public.dim_date
        """,
        conn
    )

    date_map["full_date"] = pd.to_datetime(date_map["full_date"], errors="coerce").dt.date

    purchase_date_map = date_map.rename(columns={
        "surrogate_key": "purchase_date_key",
        "full_date": "purchase_date"
    })

    delivered_date_map = date_map.rename(columns={
        "surrogate_key": "delivered_date_key",
        "full_date": "delivered_date"
    })

    estimated_date_map = date_map.rename(columns={
        "surrogate_key": "estimated_delivery_date_key",
        "full_date": "estimated_delivery_date"
    })

    return customer_map, payment_map, purchase_date_map, delivered_date_map, estimated_date_map


def load_fact_order_table(engine, conn, fact_order: pd.DataFrame) -> None:
    log.info("[load_fact_order] Load started")

    if conn is None:
        log.error("[load_fact_order] Database connection is None")
        raise LoadDataError("Database connection is None")

    if fact_order is None or fact_order.empty:
        log.error("[load_fact_order] fact_order dataframe is None or empty")
        raise LoadDataError("fact_order dataframe is None or empty")

    customer_map, payment_map, purchase_map, delivered_map, estimated_map = extract_dim_maps(conn)

    df = fact_order.copy()

    df = df.merge(customer_map, on="customer_natural_key", how="left")
    df = df.merge(payment_map, on=["payment_type", "payment_installments"], how="left")
    df = df.merge(purchase_map, on="purchase_date", how="left")
    df = df.merge(delivered_map, on="delivered_date", how="left")
    df = df.merge(estimated_map, on="estimated_delivery_date", how="left")

    missing_customer = df["customer_key"].isna().sum()
    missing_purchase = df["purchase_date_key"].isna().sum()

    if missing_customer > 0:
        log.error(f"[load_fact_order] Missing customer_key: {missing_customer}")
        raise LoadDataError(f"Missing customer_key for {missing_customer} rows")

    if missing_purchase > 0:
        log.error(f"[load_fact_order] Missing purchase_date_key: {missing_purchase}")
        raise LoadDataError(f"Missing purchase_date_key for {missing_purchase} rows")

    final_df = df[
        [
            "natural_key",
            "order_id",
            "order_status",
            "payment_value",
            "review_score",
            "delivery_days",
            "customer_key",
            "payment_key",
            "purchase_date_key",
            "delivered_date_key",
            "estimated_delivery_date_key"
        ]
    ].copy()

    try:
        log.info(f"[load_fact_order] Inserting rows: {len(final_df)}")
        final_df.to_sql(
            "fact_order",
            con=conn,
            if_exists="append",
            index=False,
            method="multi"
        )

        log.info("[load_fact_order] Load completed")
    except Exception as e:
        log.error(f"[load_fact_order] Load error: {e}")
        raise LoadDataError(f"Error loading fact_order: {e}") from e


def run_load_fact_order(engine, conn) -> None:
    log.info("[load_fact_order] Pipeline started")

    df_source = extract_fact_order_source(engine)
    fact_order = build_fact_order(df_source)
    load_fact_order_table(engine, conn, fact_order)

    dq_path = run_dq_fact_order(
        source_df=df_source,
        transformed_df=fact_order,
        engine_dw=conn
    )

    log.info(f"[load_fact_order] DQ report saved: {dq_path}")
    log.info("[load_fact_order] Pipeline completed")