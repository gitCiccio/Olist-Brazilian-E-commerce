import pandas as pd

from exception.exceptions import DataCleaningError
from logger.logger import AppLogger

log = AppLogger(name="rcl.category_translation.build", log_file="rcl_category_translation.log")


def build_rcl_product_category_translation(dataframe: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_rcl_product_category_translation] Build started")

    if dataframe is None:
        log.error("[build_rcl_product_category_translation] Input dataframe is None")
        raise DataCleaningError("Category translation dataframe is None")

    if dataframe.empty:
        log.error("[build_rcl_product_category_translation] Input dataframe is empty")
        raise DataCleaningError("Category translation dataframe is empty")

    df = dataframe.copy()

    df = df.rename(columns={
        # alias futuri, se dovessero servire
        # "product_category_name_en": "product_category_name_english",
    })

    required_cols = [
        "product_category_name",
        "product_category_name_english"
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        log.error(f"[build_rcl_product_category_translation] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing required columns: {missing}")

    df["product_category_name"] = (
        df["product_category_name"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["product_category_name_english"] = (
        df["product_category_name_english"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    before = len(df)
    df = df.drop_duplicates(subset=["product_category_name"], keep="first")
    log.info(f"[build_rcl_product_category_translation] Duplicates removed: {before - len(df)}")
    log.info(f"[build_rcl_product_category_translation] Output rows: {len(df)}")

    return df[required_cols]