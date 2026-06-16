import pandas as pd

from logger.logger import AppLogger
from exception.exceptions import DataCleaningError

log = AppLogger(name="dw.build_dim_seller", log_file="dw_load.log")


def build_dim_seller(df_rcl: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_dim_seller] Build started")

    if df_rcl is None:
        log.error("[build_dim_seller] Input dataframe is None")
        raise DataCleaningError("rcl_sellers dataframe is None")

    if df_rcl.empty:
        log.error("[build_dim_seller] Input dataframe is empty")
        raise DataCleaningError("rcl_sellers dataframe is empty")

    required_cols = [
        "seller_id",
        "seller_region",
        "seller_city",
        "seller_state"
    ]

    missing = [c for c in required_cols if c not in df_rcl.columns]
    if missing:
        log.error(f"[build_dim_seller] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing columns in rcl_sellers: {missing}")

    df = df_rcl.copy()
    input_rows = len(df)
    log.info(f"[build_dim_seller] Input rows: {input_rows}")

    null_nk_count = df["seller_id"].isna().sum()
    if null_nk_count > 0:
        log.warning(f"[build_dim_seller] Null natural keys found: {null_nk_count}")

    xx_state_count = (df["seller_state"] == "XX").sum()
    unknown_region_count = (df["seller_region"] == "unknown").sum()

    log.info(f"[build_dim_seller] seller_state='XX' rows: {xx_state_count}")
    log.info(f"[build_dim_seller] seller_region='unknown' rows: {unknown_region_count}")

    df = df.dropna(subset=["seller_id"])
    df["seller_id"] = df["seller_id"].astype(str).str.strip()

    empty_nk_mask = df["seller_id"] == ""
    empty_nk_count = empty_nk_mask.sum()
    if empty_nk_count > 0:
        log.warning(f"[build_dim_seller] Empty natural keys found after trim: {empty_nk_count}")

    df = df[~empty_nk_mask]

    df["seller_region"] = df["seller_region"].fillna("unknown").astype(str).str.strip()
    df["seller_city"] = df["seller_city"].fillna("unknown").astype(str).str.strip()
    df["seller_state"] = df["seller_state"].fillna("XX").astype(str).str.strip().str.upper()

    before_dedup_rows = len(df)
    df = df.drop_duplicates(subset=["seller_id"], keep="first")
    duplicates_removed = before_dedup_rows - len(df)

    if duplicates_removed > 0:
        log.info(f"[build_dim_seller] Duplicates removed on seller_id: {duplicates_removed}")
    else:
        log.info("[build_dim_seller] No duplicates found on seller_id")

    result = df.rename(columns={"seller_id": "natural_key"})[
        [
            "natural_key",
            "seller_region",
            "seller_city",
            "seller_state"
        ]
    ].copy()

    log.info(f"[build_dim_seller] Output rows for dim_seller: {len(result)}")
    log.info("[build_dim_seller] Build completed")

    return result