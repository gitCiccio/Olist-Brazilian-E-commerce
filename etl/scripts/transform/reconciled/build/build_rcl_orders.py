import pandas as pd

from exception.exceptions import DataCleaningError
from logger.logger import AppLogger

log = AppLogger(name="rcl.orders.build", log_file="rcl_orders.log")


def build_rcl_orders(dataframe: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_rcl_orders] Build started")

    if dataframe is None:
        log.error("[build_rcl_orders] Input dataframe is None")
        raise DataCleaningError("Orders dataframe is None")

    if dataframe.empty:
        log.error("[build_rcl_orders] Input dataframe is empty")
        raise DataCleaningError("Orders dataframe is empty")

    df = dataframe.copy()

    required_cols = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        log.error(f"[build_rcl_orders] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing required columns: {missing}")

    log.info(f"[build_rcl_orders] Input rows: {len(df)}")

    for col in ["order_id", "customer_id"]:
        df[col] = df[col].astype(str).str.strip()

    df["order_status"] = (
        df["order_status"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    ts_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in ts_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    before = len(df)
    df = df.drop_duplicates()
    log.info(f"[build_rcl_orders] Exact duplicates removed: {before - len(df)}")
    log.info(f"[build_rcl_orders] Output rows: {len(df)}")

    return df[required_cols]