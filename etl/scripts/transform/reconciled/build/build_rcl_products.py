import pandas as pd

from exception.exceptions import DataCleaningError
from logger.logger import AppLogger

log = AppLogger(name="rcl.products.build", log_file="rcl_products.log")


def build_rcl_products(dataframe: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_rcl_products] Build started")

    if dataframe is None:
        log.error("[build_rcl_products] Input dataframe is None")
        raise DataCleaningError("Products dataframe is None")

    if dataframe.empty:
        log.error("[build_rcl_products] Input dataframe is empty")
        raise DataCleaningError("Products dataframe is empty")

    df = dataframe.copy()

    df = df.rename(columns={
        "product_description_lenght": "product_description_length"
    })

    required_cols = [
        "product_id",
        "product_category_name",
        "product_name_length",
        "product_description_length",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        log.error(f"[build_rcl_products] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing required columns: {missing}")

    log.info(f"[build_rcl_products] Input rows: {len(df)}")

    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["product_category_name"] = (
        df["product_category_name"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    numeric_cols = [
        "product_name_length",
        "product_description_length",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    before = len(df)
    df = df.drop_duplicates()
    log.info(f"[build_rcl_products] Exact duplicates removed: {before - len(df)}")
    log.info(f"[build_rcl_products] Output rows: {len(df)}")

    return df[required_cols]