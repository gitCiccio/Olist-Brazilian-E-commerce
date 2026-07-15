import pandas as pd
from sqlalchemy import text

from etl.scripts.data_quality.dq_dim_product import run_dq_dim_product
from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError
from etl.scripts.load.build.build_dim_product import build_dim_product

log = AppLogger(name="dw.load_dim_product", log_file="dw_load.log")


def extract_rcl_products(engine) -> pd.DataFrame:
    """
    Estrae i dati dei prodotti dall'area reconciled. Effettua una JOIN 
    con `rcl_product_category_translation` per ottenere direttamente 
    la categoria in inglese.

    :param engine: Connessione al database (schema reconciled).
    :return: DataFrame Pandas con i dati dei prodotti arricchiti.
    """
    log.info("[load_dim_product] Extract from rcl_products started")

    if engine is None:
        log.error("[load_dim_product] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
        p.product_id AS natural_key,
        t.product_category_name_english AS category_name_en,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    FROM reconciled.rcl_products p
    LEFT JOIN reconciled.rcl_product_category_translation t
        ON p.product_category_name = t.product_category_name
    """

    try:
        df_rcl = pd.read_sql(query, engine)
        log.info(f"[load_dim_product] Rows extracted from rcl_products: {len(df_rcl)}")
        return df_rcl

    except Exception as e:
        log.error(f"[load_dim_product] Error during extract from rcl_products: {e}")
        raise ExtractDataError(f"Error extracting rcl_products: {e}") from e


def load_dim_product_table(conn, dim_product: pd.DataFrame) -> None:
    """
    Carica i dati della dimensione nella tabella `dim_product` del Data Warehouse.
    Nota: la TRUNCATE della tabella è gestita dall'orchestratore, qui si esegue solo l'inserimento in append.

    :param conn: Connessione al database (schema public/dwh).
    :param dim_product: DataFrame Pandas con i dati pronti per il DWH.
    """
    log.info("[load_dim_product] Load into dim_product started")

    if conn is None:
        log.error("[load_dim_product] Database connection is None")
        raise LoadDataError("Database connection is None")

    if dim_product is None:
        log.error("[load_dim_product] dim_product dataframe is None")
        raise LoadDataError("dim_product dataframe is None")

    if dim_product.empty:
        log.error("[load_dim_product] dim_product dataframe is empty")
        raise LoadDataError("dim_product dataframe is empty")

    required_cols = [
        "natural_key",
        "category_name_en",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    missing = [c for c in required_cols if c not in dim_product.columns]
    if missing:
        log.error(f"[load_dim_product] Missing required columns in dim_product: {missing}")
        raise LoadDataError(f"Missing required columns in dim_product: {missing}")

    try:

        log.info(f"[load_dim_product] Inserting rows into dim_product: {len(dim_product)}")
        dim_product.to_sql(
            "dim_product",
            con=conn,
            if_exists="append",
            index=False,
            method="multi"
        )

        log.info("[load_dim_product] Load into dim_product completed")

    except Exception as e:
        log.error(f"[load_dim_product] Error during load into dim_product: {e}")
        raise LoadDataError(f"Error loading dim_product: {e}") from e


def run_load_dim_product(engine, conn) -> None:
    """
    Esegue l'intero flusso di caricamento per `dim_product`:
    1. Extract dei prodotti con relative traduzioni da reconciled.
    2. Build (generazione delle chiavi, sostituzione nulli con default, ecc.).
    3. Load nel DWH.
    4. Esecuzione dei controlli di Data Quality (DQ) post-caricamento.

    :param engine: Connessione in lettura (reconciled).
    :param conn: Connessione in scrittura (dwh).
    """
    log.info("[load_dim_product] Pipeline started")

    df_rcl = extract_rcl_products(engine)
    dim_product = build_dim_product(df_rcl)
    load_dim_product_table(conn, dim_product)

    dq_path = run_dq_dim_product(
        source_df=df_rcl,
        transformed_df=dim_product,
        engine_dw=conn
    )
    log.info(f"[load_dim_product] DQ report saved: {dq_path}")

    log.info("[load_dim_product] Pipeline completed")