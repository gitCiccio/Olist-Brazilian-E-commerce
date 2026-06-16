import pandas as pd

from logger.logger import AppLogger
from exception.exceptions import DataCleaningError

log = AppLogger(name="dw.build_fact_order", log_file="dw_load.log")


def build_fact_order(df_rcl: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_fact_order] Build started")

    if df_rcl is None:
        log.error("[build_fact_order] Input dataframe is None")
        raise DataCleaningError("fact_order dataframe is None")

    if df_rcl.empty:
        log.error("[build_fact_order] Input dataframe is empty")
        raise DataCleaningError("fact_order dataframe is empty")

    required_cols = [
        "order_id",
        "order_status",
        "customer_natural_key",
        "payment_type",
        "payment_installments",
        "payment_value",
        "review_score",
        "purchase_date",
        "delivered_date",
        "estimated_delivery_date"
    ]

    missing = [c for c in required_cols if c not in df_rcl.columns]
    if missing:
        log.error(f"[build_fact_order] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing columns in fact_order source: {missing}")

    df = df_rcl.copy()
    log.info(f"[build_fact_order] Input rows: {len(df)}")

    df["order_id"] = df["order_id"].astype(str).str.strip()
    df["order_status"] = df["order_status"].fillna("unknown").astype(str).str.strip().str.lower()
    df["customer_natural_key"] = df["customer_natural_key"].astype(str).str.strip()

    df["payment_type"] = df["payment_type"].fillna("not_defined").astype(str).str.strip().str.lower()
    df["payment_installments"] = pd.to_numeric(df["payment_installments"], errors="coerce").fillna(0).astype(int)
    df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce").fillna(0).round(2)
    df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce").round(1)

    df["purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce").dt.date
    df["delivered_date"] = pd.to_datetime(df["delivered_date"], errors="coerce").dt.date
    df["estimated_delivery_date"] = pd.to_datetime(df["estimated_delivery_date"], errors="coerce").dt.date

    df = df[df["order_id"] != ""]
    df = df[df["customer_natural_key"] != ""]

    df["delivery_days"] = (
        pd.to_datetime(df["delivered_date"], errors="coerce") -
        pd.to_datetime(df["purchase_date"], errors="coerce")
    ).dt.days

    negative_delivery = df["delivery_days"].dropna().lt(0).sum()
    if negative_delivery > 0:
        log.warning(f"[build_fact_order] Negative delivery_days found: {negative_delivery}")

    before_dedup = len(df)
    df = df.drop_duplicates(subset=["order_id"], keep="first")
    log.info(f"[build_fact_order] Duplicates removed on order_id: {before_dedup - len(df)}")

    df["natural_key"] = df["order_id"]

    result = df[
        [
            "natural_key",
            "order_id",
            "order_status",
            "payment_value",
            "review_score",
            "delivery_days",
            "customer_natural_key",
            "payment_type",
            "payment_installments",
            "purchase_date",
            "delivered_date",
            "estimated_delivery_date"
        ]
    ].copy()

    log.info(f"[build_fact_order] Output rows: {len(result)}")
    log.info("[build_fact_order] Build completed")

    return result