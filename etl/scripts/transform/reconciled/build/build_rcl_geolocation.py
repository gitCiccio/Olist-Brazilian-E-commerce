from unidecode import unidecode
import pandas as pd

from exception.exceptions import DataCleaningError
from logger.logger import AppLogger
from etl.scripts.transform.reconciled.build.build_rcl_customers import STATE_REGEX

log = AppLogger(name="rcl.geolocation.build", log_file="rcl_geolocation.log")


def build_rcl_geolocation(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Esegue la pulizia e l'arricchimento dei dati di geolocalizzazione (CAP, coordinate, città, stato).
    - Standardizza i nomi delle città (minuscolo, senza accenti, trim).
    - Valida e formatta la sigla dello stato.
    - Converte le coordinate geografiche (latitudine, longitudine) in valori numerici, 
      forzando a NaN i valori invalidi.
    - Rimuove eventuali duplicati esatti.

    :param dataframe: DataFrame Pandas contenente i dati raw di geolocalizzazione dallo staging.
    :return: DataFrame Pandas pulito e formattato per l'area reconciled.
    """
    log.info("[build_rcl_geolocation] Build started")

    if dataframe is None:
        log.error("[build_rcl_geolocation] Input dataframe is None")
        raise DataCleaningError("Geolocation dataframe is None")

    if dataframe.empty:
        log.error("[build_rcl_geolocation] Input dataframe is empty")
        raise DataCleaningError("Geolocation dataframe is empty")

    df = dataframe.copy()

    df = df.rename(columns={
        # alias futuri, se dovessero comparire
        # "geolocation_zipcode_prefix": "geolocation_zip_code_prefix",
    })

    required_cols = [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state"
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        log.error(f"[build_rcl_geolocation] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing required columns: {missing}")

    df["geolocation_city"] = (
        df["geolocation_city"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
        .apply(unidecode)
    )

    df["geolocation_state"] = (
        df["geolocation_state"]
        .fillna("XX")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    invalid_mask = ~df["geolocation_state"].str.match(STATE_REGEX, na=False)
    invalid_count = invalid_mask.sum()
    if invalid_count > 0:
        log.warning(f"[build_rcl_geolocation] Invalid geolocation_state: {invalid_count} -> 'XX'")
        df.loc[invalid_mask, "geolocation_state"] = "XX"

    df["geolocation_lat"] = pd.to_numeric(df["geolocation_lat"], errors="coerce")
    df["geolocation_lng"] = pd.to_numeric(df["geolocation_lng"], errors="coerce")

    before = len(df)
    df = df.drop_duplicates()
    log.info(f"[build_rcl_geolocation] Exact duplicates removed: {before - len(df)}")
    log.info(f"[build_rcl_geolocation] Output rows: {len(df)}")

    return df[required_cols]