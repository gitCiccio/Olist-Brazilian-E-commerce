import pandas as pd
from sqlalchemy import text

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="rcl.products.load", log_file="rcl_products.log")


def extract_products_from_staging(engine) -> pd.DataFrame:
    """
    Estrae tutti i record dei prodotti dalla tabella `stg_products` (area di staging).
    
    :param engine: Connessione al database di staging.
    :return: DataFrame Pandas con i dati estratti.
    """
    log.info("[load_rcl_products] Extract from products started")

    if engine is None:
        log.error("[load_rcl_products] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
            SELECT product_id,
                   product_category_name,
                   product_name_length,
                   product_description_lenght,
                   product_photos_qty,
                   product_weight_g,
                   product_length_cm,
                   product_height_cm,
                   product_width_cm
            FROM staging.stg_products
            """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_rcl_products] Rows extracted: {len(df)}")
        return df
    except Exception as e:
        log.error(f"[load_rcl_products] Error during extract: {e}")
        raise ExtractDataError(f"Error extracting products: {e}") from e


def load_rcl_products_table(conn, df_rcl: pd.DataFrame) -> None:
    """
    Carica i dati dei prodotti trasformati nella tabella `rcl_products` dell'area reconciled.
    Esegue prima una TRUNCATE per garantire l'idempotenza.

    :param conn: Connessione al database (reconciled).
    :param df_rcl: DataFrame Pandas con i dati puliti.
    """
    log.info("[load_rcl_products] Load into rcl_products started")

    if conn is None:
        log.error("[load_rcl_products] Database connection is None")
        raise LoadDataError("Database connection is None")

    if df_rcl is None or df_rcl.empty:
        log.error("[load_rcl_products] rcl_products dataframe is empty or None")
        raise LoadDataError("rcl_products dataframe is empty or None")

    try:
        conn.execute(text("TRUNCATE TABLE reconciled.rcl_products"))
        df_rcl.to_sql("rcl_products", con=conn, schema="reconciled", if_exists="append", index=False, method="multi")
        log.info(f"[load_rcl_products] Loaded rows: {len(df_rcl)}")
    except Exception as e:
        log.error(f"[load_rcl_products] Error during load: {e}")
        raise LoadDataError(f"Error loading rcl_products: {e}") from e