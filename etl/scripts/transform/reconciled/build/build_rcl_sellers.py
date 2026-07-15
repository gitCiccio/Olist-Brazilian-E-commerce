from unidecode import unidecode
import pandas as pd

from exception.exceptions import DataCleaningError
from logger.logger import AppLogger
from etl.scripts.transform.reconciled.build.build_rcl_customers import BRAZIL_STATE_TO_REGION, STATE_REGEX

log = AppLogger(name="rcl.sellers.build", log_file="rcl_sellers.log")


def build_rcl_sellers(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Esegue la pulizia e l'arricchimento dei dati relativi ai venditori (sellers).
    - Standardizza i nomi delle città (minuscolo, senza accenti, trim).
    - Valida e formatta la sigla dello stato, associandola a una regione geografica (es. 'sudeste').
    - Rimuove eventuali duplicati esatti.

    :param dataframe: DataFrame Pandas contenente i dati raw dei venditori dallo staging.
    :return: DataFrame Pandas pulito e arricchito per l'area reconciled.
    """
    log.info("[build_rcl_sellers] Build started")

    if dataframe is None:
        log.error("[build_rcl_sellers] Input dataframe is None")
        raise DataCleaningError("Sellers dataframe is None")

    if dataframe.empty:
        log.error("[build_rcl_sellers] Input dataframe is empty")
        raise DataCleaningError("Sellers dataframe is empty")

    df = dataframe.copy()

    df = df.rename(columns={
        # alias futuri, se dovessero servire
        # "seller_zipcode_prefix": "seller_zip_code_prefix",
    })

    required_cols = [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state"
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        log.error(f"[build_rcl_sellers] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing required columns: {missing}")

    log.info(f"[build_rcl_sellers] Input rows: {len(df)}")

    df["seller_city"] = (
        df["seller_city"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
        .apply(unidecode)
    )

    df["seller_state"] = (
        df["seller_state"]
        .fillna("XX")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    invalid_mask = ~df["seller_state"].str.match(STATE_REGEX, na=False)
    invalid_count = invalid_mask.sum()
    if invalid_count > 0:
        log.warning(f"[build_rcl_sellers] Invalid seller_state: {invalid_count} -> 'XX'")
        df.loc[invalid_mask, "seller_state"] = "XX"

    df["seller_region"] = df["seller_state"].map(BRAZIL_STATE_TO_REGION).fillna("unknown")
    df["state_valid_flag"] = df["seller_state"] != "XX"

    before = len(df)
    df = df.drop_duplicates()
    log.info(f"[build_rcl_sellers] Exact duplicates removed: {before - len(df)}")
    log.info(f"[build_rcl_sellers] Output rows: {len(df)}")

    return df[[
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
        "seller_region",
        "state_valid_flag"
    ]]