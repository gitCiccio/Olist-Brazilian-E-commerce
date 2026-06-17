import pandas as pd

from exception.exceptions import DataCleaningError
from logger.logger import AppLogger

log = AppLogger(name="rcl.order_items.build", log_file="rcl_order_items.log")


def build_rcl_order_items(dataframe: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_rcl_order_items] Build started")

    if dataframe is None:
        log.error("[build_rcl_order_items] Input dataframe is None")
        raise DataCleaningError("Order items dataframe is None")

    if dataframe.empty:
        log.error("[build_rcl_order_items] Input dataframe is empty")
        raise DataCleaningError("Order items dataframe is empty")

    df = dataframe.copy()

    df = df.rename(columns={
        # alias futuri, se dovessero servire
        # "shipping_date_limit": "shipping_limit_date",
    })

    required_cols = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value"
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        log.error(f"[build_rcl_order_items] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing required columns: {missing}")

    log.info(f"[build_rcl_order_items] Input rows: {len(df)}")

    for col in ["order_id", "product_id", "seller_id"]:
        df[col] = df[col].astype(str).str.strip()

    df["order_item_id"] = pd.to_numeric(df["order_item_id"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["freight_value"] = pd.to_numeric(df["freight_value"], errors="coerce")
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")

    before = len(df)
    df = df.drop_duplicates()
    log.info(f"[build_rcl_order_items] Exact duplicates removed: {before - len(df)}")
    log.info(f"[build_rcl_order_items] Output rows: {len(df)}")

    return df[required_cols]