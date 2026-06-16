import pandas as pd

from logger.logger import AppLogger
from exception.exceptions import DataCleaningError

log = AppLogger(name="dw.build_dim_product", log_file="dw_load.log")


def build_dim_product(df_rcl: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_dim_product] Build started")

    if df_rcl is None:
        log.error("[build_dim_product] Input dataframe is None")
        raise DataCleaningError("rcl_products dataframe is None")

    if df_rcl.empty:
        log.error("[build_dim_product] Input dataframe is empty")
        raise DataCleaningError("rcl_products dataframe is empty")

    required_cols = [
        "natural_key",
        "category_name_en"
    ]

    missing = [c for c in required_cols if c not in df_rcl.columns]
    if missing:
        log.error(f"[build_dim_product] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing columns in rcl_products: {missing}")

    df = df_rcl.copy()
    input_rows = len(df)
    log.info(f"[build_dim_product] Input rows: {input_rows}")

    null_nk_count = df["natural_key"].isna().sum()
    if null_nk_count > 0:
        log.warning(f"[build_dim_product] Null natural keys found: {null_nk_count}")

    df = df.dropna(subset=["natural_key"])
    df["natural_key"] = df["natural_key"].astype(str).str.strip()

    empty_nk_mask = df["natural_key"] == ""
    empty_nk_count = empty_nk_mask.sum()
    if empty_nk_count > 0:
        log.warning(f"[build_dim_product] Empty natural keys found after trim: {empty_nk_count}")

    df = df[~empty_nk_mask]

    null_category_count = df["category_name_en"].isna().sum()
    if null_category_count > 0:
        log.warning(f"[build_dim_product] Null category_name_en found: {null_category_count}")

    df["category_name_en"] = (
        df["category_name_en"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
    )

    empty_category_mask = df["category_name_en"] == ""
    empty_category_count = empty_category_mask.sum()
    if empty_category_count > 0:
        log.warning(
            f"[build_dim_product] Empty category_name_en found after trim: {empty_category_count}"
        )
        df.loc[empty_category_mask, "category_name_en"] = "unknown"

    before_dedup_rows = len(df)
    df = df.drop_duplicates(subset=["natural_key"], keep="first")
    duplicates_removed = before_dedup_rows - len(df)

    if duplicates_removed > 0:
        log.info(f"[build_dim_product] Duplicates removed on natural_key: {duplicates_removed}")
    else:
        log.info("[build_dim_product] No duplicates found on natural_key")

    result = df[[
        "natural_key",
        "category_name_en"
    ]].copy()

    log.info(f"[build_dim_product] Output rows for dim_product: {len(result)}")
    log.info("[build_dim_product] Build completed")

    return result