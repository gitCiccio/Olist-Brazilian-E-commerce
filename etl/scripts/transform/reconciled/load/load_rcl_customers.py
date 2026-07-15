import pandas as pd
from sqlalchemy import text

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="rcl.customers.load", log_file="rcl_customers.log")


def extract_customers_from_staging(engine) -> pd.DataFrame:
    """
    Estrae tutti i record dalla tabella `stg_customers` (area di staging).
    
    :param engine: Connessione al database di staging.
    :return: DataFrame Pandas con i dati estratti.
    """
    log.info("[load_rcl_customers] Extract from staging customers started")

    if engine is None:
        log.error("[load_rcl_customers] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            customer_id,
            customer_unique_id,
            customer_zip_code_prefix,
            customer_city,
            customer_state
        FROM staging.stg_customers
    """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_rcl_customers] Rows extracted from customers: {len(df)}")
        return df

    except Exception as e:
        log.error(f"[load_rcl_customers] Error during extract from customers: {e}")
        raise ExtractDataError(f"Error extracting customers: {e}") from e


def load_rcl_customers_table(conn, df_rcl: pd.DataFrame) -> None:
    """
    Carica i dati trasformati nella tabella `rcl_customers` dell'area reconciled.
    Esegue prima una TRUNCATE per sostituire l'intero dataset, garantendo l'idempotenza 
    dell'operazione in caso di riesecuzione della pipeline.

    :param conn: Connessione al database (reconciled).
    :param df_rcl: DataFrame Pandas con i dati puliti e arricchiti.
    """
    log.info("[load_rcl_customers] Load into rcl_customers started")

    if conn is None:
        log.error("[load_rcl_customers] Database connection is None")
        raise LoadDataError("Database connection is None")

    if df_rcl is None:
        log.error("[load_rcl_customers] rcl_customers dataframe is None")
        raise LoadDataError("rcl_customers dataframe is None")

    if df_rcl.empty:
        log.error("[load_rcl_customers] rcl_customers dataframe is empty")
        raise LoadDataError("rcl_customers dataframe is empty")

    required_cols = [
        'customer_id',
        'customer_unique_id',
        'customer_zip_code_prefix',
        'customer_city',
        'customer_state',
        'customer_region',
        'state_valid_flag'
    ]
    missing = [c for c in required_cols if c not in df_rcl.columns]
    if missing:
        log.error(f"[load_rcl_customers] Missing required columns: {missing}")
        raise LoadDataError(f"Missing required columns in rcl_customers: {missing}")

    try:
        log.info("[load_rcl_customers] Truncating rcl_customers")
        conn.execute(text("TRUNCATE TABLE reconciled.rcl_customers"))

        log.info(f"[load_rcl_customers] Inserting rows into rcl_customers: {len(df_rcl)}")
        df_rcl.to_sql(
            "rcl_customers",
            con=conn,
            schema="reconciled",
            if_exists="append",
            index=False,
            method="multi"
        )

        log.info("[load_rcl_customers] Load into rcl_customers completed")

    except Exception as e:
        log.error(f"[load_rcl_customers] Error during load into rcl_customers: {e}")
        raise LoadDataError(f"Error loading rcl_customers: {e}") from e