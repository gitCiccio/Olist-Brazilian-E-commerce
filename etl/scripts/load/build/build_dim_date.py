import pandas as pd

from logger.logger import AppLogger
from exception.exceptions import DataCleaningError

log = AppLogger(name="dw.build_dim_date", log_file="dw_load.log")


def build_dim_date(df_dates: pd.DataFrame) -> pd.DataFrame:
    """
    Costruisce la dimensione temporale a partire da un elenco di date univoche.
    - Converte le date in formato `datetime` (normalizzate a mezzanotte).
    - Rimuove le date non valide o mancanti.
    - Estrae attributi temporali utili per le analisi (giorno, mese, anno, trimestre, ecc.).
    - Crea una `natural_key` intera in formato YYYYMMDD.

    :param df_dates: DataFrame Pandas contenente l'elenco delle date distinte.
    :return: DataFrame Pandas arricchito con gli attributi temporali.
    """
    log.info("[build_dim_date] Build started")

    if df_dates is None:
        log.error("[build_dim_date] Input dataframe is None")
        raise DataCleaningError("date dataframe is None")

    if df_dates.empty:
        log.error("[build_dim_date] Input dataframe is empty")
        raise DataCleaningError("date dataframe is empty")

    required_cols = ["full_date"]
    missing = [c for c in required_cols if c not in df_dates.columns]
    if missing:
        log.error(f"[build_dim_date] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing columns in date dataframe: {missing}")

    df = df_dates.copy()
    input_rows = len(df)
    log.info(f"[build_dim_date] Input rows: {input_rows}")

    df["full_date"] = pd.to_datetime(df["full_date"], errors="coerce").dt.normalize()

    invalid_date_count = df["full_date"].isna().sum()
    if invalid_date_count > 0:
        log.warning(f"[build_dim_date] Invalid dates found: {invalid_date_count}")

    df = df.dropna(subset=["full_date"])

    before_dedup_rows = len(df)
    df = df.drop_duplicates(subset=["full_date"]).sort_values("full_date").reset_index(drop=True)
    duplicates_removed = before_dedup_rows - len(df)

    if duplicates_removed > 0:
        log.info(f"[build_dim_date] Duplicate dates removed: {duplicates_removed}")
    else:
        log.info("[build_dim_date] No duplicate dates found")

    week_of_year = df["full_date"].dt.isocalendar().week.astype(int)
    day_of_week = (df["full_date"].dt.dayofweek + 1).astype(int)

    result = pd.DataFrame({
        "natural_key": df["full_date"].dt.strftime("%Y%m%d").astype(int),
        "full_date": df["full_date"].dt.date,
        "day": df["full_date"].dt.day.astype(int),
        "month": df["full_date"].dt.month.astype(int),
        "quarter": df["full_date"].dt.quarter.astype(int),
        "year": df["full_date"].dt.year.astype(int),
        "day_of_week": day_of_week,
        "week_of_year": week_of_year,
        "is_weekend": day_of_week.isin([6, 7])
    })

    log.info(f"[build_dim_date] Output rows for dim_date: {len(result)}")
    log.info("[build_dim_date] Build completed")

    return result