import pandas as pd
from sqlalchemy import text
from etl.scripts.data_quality.dq_fact_sale_item import run_dq_fact_sale_item
from etl.scripts.load.build.build_fact_sale_item import build_fact_sale_item
from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="dw.load_fact_sale_item", log_file="dw_load.log")


def extract_fact_sale_item_source(engine) -> pd.DataFrame:
    log.info("[load_fact_sale_item] Extract started")

    if engine is None:
        log.error("[load_fact_sale_item] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            oi.order_id,
            oi.order_item_id,
            o.order_status,
            oi.product_id AS product_natural_key,
            c.customer_unique_id AS customer_natural_key,
            oi.seller_id AS seller_natural_key,
            oi.price,
            oi.freight_value,
            CAST(o.order_purchase_timestamp AS DATE) AS purchase_date,
            CAST(oi.shipping_limit_date AS DATE) AS shipping_limit_date,
            CAST(o.order_delivered_customer_date AS DATE) AS delivered_date,
            CAST(o.order_estimated_delivery_date AS DATE) AS estimated_delivery_date
        FROM rcl_order_items oi
        JOIN rcl_orders o
            ON oi.order_id = o.order_id
        JOIN rcl_customers c
            ON o.customer_id = c.customer_id
    """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_fact_sale_item] Rows extracted: {len(df)}")
        return df
    except Exception as e:
        log.error(f"[load_fact_sale_item] Extract error: {e}")
        raise ExtractDataError(f"Error extracting fact_sale_item source: {e}") from e


def extract_dim_maps(engine):
    product_map = pd.read_sql(
        """
        SELECT natural_key, surrogate_key
        FROM dim_product
        """,
        engine
    ).rename(columns={"natural_key": "product_natural_key", "surrogate_key": "product_key"})

    customer_map = pd.read_sql(
        """
        SELECT natural_key, surrogate_key
        FROM dim_customer
        WHERE is_current = TRUE
        """,
        engine
    ).rename(columns={"natural_key": "customer_natural_key", "surrogate_key": "customer_key"})

    seller_map = pd.read_sql(
        """
        SELECT natural_key, surrogate_key
        FROM dim_seller
        WHERE is_current = TRUE
        """,
        engine
    ).rename(columns={"natural_key": "seller_natural_key", "surrogate_key": "seller_key"})

    date_map = pd.read_sql(
        """
        SELECT surrogate_key, full_date
        FROM dim_date
        """,
        engine
    )
    date_map["full_date"] = pd.to_datetime(date_map["full_date"], errors="coerce").dt.date

    purchase_map = date_map.rename(columns={"surrogate_key": "purchase_date_key", "full_date": "purchase_date"})
    shipping_map = date_map.rename(columns={"surrogate_key": "shipping_limit_date_key", "full_date": "shipping_limit_date"})
    delivered_map = date_map.rename(columns={"surrogate_key": "delivered_date_key", "full_date": "delivered_date"})
    estimated_map = date_map.rename(columns={"surrogate_key": "estimated_delivery_date_key", "full_date": "estimated_delivery_date"})

    return product_map, customer_map, seller_map, purchase_map, shipping_map, delivered_map, estimated_map


def load_fact_sale_item_table(engine, conn, fact_sale_item: pd.DataFrame) -> None:
    log.info("[load_fact_sale_item] Load started")

    if conn is None:
        log.error("[load_fact_sale_item] Database connection is None")
        raise LoadDataError("Database connection is None")

    if fact_sale_item is None or fact_sale_item.empty:
        log.error("[load_fact_sale_item] fact_sale_item dataframe is None or empty")
        raise LoadDataError("fact_sale_item dataframe is None or empty")

    (
        product_map,
        customer_map,
        seller_map,
        purchase_map,
        shipping_map,
        delivered_map,
        estimated_map
    ) = extract_dim_maps(engine)

    df = fact_sale_item.copy()

    df = df.merge(product_map, on="product_natural_key", how="left")
    df = df.merge(customer_map, on="customer_natural_key", how="left")
    df = df.merge(seller_map, on="seller_natural_key", how="left")
    df = df.merge(purchase_map, on="purchase_date", how="left")
    df = df.merge(shipping_map, on="shipping_limit_date", how="left")
    df = df.merge(delivered_map, on="delivered_date", how="left")
    df = df.merge(estimated_map, on="estimated_delivery_date", how="left")

    missing_product = df["product_key"].isna().sum()
    missing_customer = df["customer_key"].isna().sum()
    missing_seller = df["seller_key"].isna().sum()
    missing_purchase = df["purchase_date_key"].isna().sum()

    if missing_product > 0:
        raise LoadDataError(f"Missing product_key for {missing_product} rows")
    if missing_customer > 0:
        raise LoadDataError(f"Missing customer_key for {missing_customer} rows")
    if missing_seller > 0:
        raise LoadDataError(f"Missing seller_key for {missing_seller} rows")
    if missing_purchase > 0:
        raise LoadDataError(f"Missing purchase_date_key for {missing_purchase} rows")

    final_df = df[
        [
            "natural_key",
            "order_id",
            "order_item_id",
            "order_status",
            "item_count",
            "price",
            "freight_value",
            "product_key",
            "customer_key",
            "seller_key",
            "purchase_date_key",
            "shipping_limit_date_key",
            "delivered_date_key",
            "estimated_delivery_date_key"
        ]
    ].copy()

    try:
        log.info("[load_fact_sale_item] Truncating fact_sale_item")
        conn.execute(text("TRUNCATE TABLE fact_sale_item"))

        log.info(f"[load_fact_sale_item] Inserting rows: {len(final_df)}")
        final_df.to_sql(
            "fact_sale_item",
            con=conn,
            if_exists="append",
            index=False,
            method="multi"
        )

        log.info("[load_fact_sale_item] Load completed")
    except Exception as e:
        log.error(f"[load_fact_sale_item] Load error: {e}")
        raise LoadDataError(f"Error loading fact_sale_item: {e}") from e


def run_load_fact_sale_item(engine, conn) -> None:
    log.info("[load_fact_sale_item] Pipeline started")

    df_source = extract_fact_sale_item_source(engine)
    fact_sale_item = build_fact_sale_item(df_source)
    load_fact_sale_item_table(engine, conn, fact_sale_item)

    dq_path = run_dq_fact_sale_item(
        source_df=df_source,
        transformed_df=fact_sale_item,
        engine_dw=conn
    )
    log.info(f"[load_fact_sale_item] DQ report saved: {dq_path}")

    log.info("[load_fact_sale_item] Pipeline completed")