import pandas as pd

from logger.logger import AppLogger
from exception.exceptions import DataCleaningError

log = AppLogger(name="dw.build_fact_sale_item", log_file="dw_load.log")


def build_fact_sale_item(df_rcl: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_fact_sale_item] Build started")

    if df_rcl is None:
        log.error("[build_fact_sale_item] Input dataframe is None")
        raise DataCleaningError("fact_sale_item dataframe is None")

    if df_rcl.empty:
        log.error("[build_fact_sale_item] Input dataframe is empty")
        raise DataCleaningError("fact_sale_item dataframe is empty")

    required_cols = [
        "order_id",
        "order_item_id",
        "order_status",
        "product_natural_key",
        "customer_natural_key",
        "seller_natural_key",
        "price",
        "freight_value",
        "purchase_date",
        "shipping_limit_date",
        "delivered_date",
        "estimated_delivery_date"
    ]

    missing = [c for c in required_cols if c not in df_rcl.columns]
    if missing:
        log.error(f"[build_fact_sale_item] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing columns in fact_sale_item source: {missing}")

    df = df_rcl.copy()
    log.info(f"[build_fact_sale_item] Input rows: {len(df)}")

    df["order_id"] = df["order_id"].astype(str).str.strip()
    df["order_item_id"] = pd.to_numeric(df["order_item_id"], errors="coerce").astype("Int64")
    df["order_status"] = df["order_status"].fillna("unknown").astype(str).str.strip().str.lower()

    df["product_natural_key"] = df["product_natural_key"].astype(str).str.strip()
    df["customer_natural_key"] = df["customer_natural_key"].astype(str).str.strip()
    df["seller_natural_key"] = df["seller_natural_key"].astype(str).str.strip()

    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0).round(2)
    df["freight_value"] = pd.to_numeric(df["freight_value"], errors="coerce").fillna(0).round(2)
    df["item_count"] = 1

    df["purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce").dt.date
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce").dt.date
    df["delivered_date"] = pd.to_datetime(df["delivered_date"], errors="coerce").dt.date
    df["estimated_delivery_date"] = pd.to_datetime(df["estimated_delivery_date"], errors="coerce").dt.date

    df = df.dropna(subset=["order_item_id"])
    df["order_item_id"] = df["order_item_id"].astype(int)

    df = df[df["order_id"] != ""]
    df = df[df["product_natural_key"] != ""]
    df = df[df["customer_natural_key"] != ""]
    df = df[df["seller_natural_key"] != ""]

    df["natural_key"] = df["order_id"] + "-" + df["order_item_id"].astype(str)

    before_dedup = len(df)
    df = df.drop_duplicates(subset=["natural_key"], keep="first")
    log.info(f"[build_fact_sale_item] Duplicates removed on natural_key: {before_dedup - len(df)}")

    result = df[
        [
            "natural_key",
            "order_id",
            "order_item_id",
            "order_status",
            "item_count",
            "price",
            "freight_value",
            "product_natural_key",
            "customer_natural_key",
            "seller_natural_key",
            "purchase_date",
            "shipping_limit_date",
            "delivered_date",
            "estimated_delivery_date"
        ]
    ].copy()

    log.info(f"[build_fact_sale_item] Output rows: {len(result)}")
    log.info("[build_fact_sale_item] Build completed")

    return result