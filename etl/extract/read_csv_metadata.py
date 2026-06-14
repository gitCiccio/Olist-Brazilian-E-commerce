"""
Lo script read_csv_metadata.py ha lo scopo di eseguire un controllo preliminare tecnico.
Verifica che i csv siano compatibili con ciò che noi ci aspettiamo e che restituisca le informazioni necessarie

Evita di capire tardi se i dati che stiamo estraendo sono presenti o meno
Generalmente è uno script che si occupa di eseguire i seguenti controlli:
    - Verifica se il file esiste ed è leggibile
    - Se le colonne attese sono tutte presenti
    - Indica quali sono le colonne presenti
    - Indica il numero di righe contenuto nel file
    - Indica quali colonne devono essere lette nei batch

Quello che fa in sostanza si chiama -> ispezione tecnica
"""
import pandas as pd
from logger.logger import AppLogger
from exception.exceptions import ExtractDataError
from etl.extract.models import CsvMetadata

log = AppLogger(name="read_csv_metadata.extract", log_file="read_csv_metadata.log")

def read_csv_metadata(csv_path: str, required_columns: list[str] | None = None) -> CsvMetadata:
    log.info(f"[read_csv_metadata] Reading csv {csv_path}")

    # Lettura delle colonne disponibili del CSV
    # header_df è semplicemente un df vuoto
    # Contenete solo i nomi delle colonne
    try:
        header_df = pd.read_csv(csv_path, nrows=0)
    except FileNotFoundError as e:
        log.error(f"[read_csv_metadata] File not found: {csv_path}")
        raise ExtractDataError(f"File not found: {csv_path}") from e
    except UnicodeDecodeError as e:
        log.error(f"[read_csv_metadata] Encoding error while reading header: {csv_path}")
        raise ExtractDataError(f"Encoding error while reading header: {csv_path}") from e
    except Exception as e:
        log.error(f"[read_csv_metadata] Error while reading header from {csv_path}: {e}")
        raise ExtractDataError(f"Error while reading header from {csv_path}: {e}") from e

    # Prendiamo le colonne disponibili presenti sul CSV
    available_list_columns = header_df.columns.to_list()
    log.info(f"[read_csv_metadata] Available columns in {csv_path}: {available_list_columns}")

    # fallback se required_columns è None, in questo modo consideriamo tutte le colonne disponibili
    if required_columns is None:
        log.warning(f"[read_csv_metadata] Required columns {required_columns} is None")
        required_columns = available_list_columns

    # Verifichiamo se le colonne che ci interessano per l'analisi
    # Sono presenti dentro le colonne del CSV
    missing_cols = [col for col in required_columns if col not in available_list_columns]
    if missing_cols:
        log.error(f"[read_csv_metadata] Missing columns in {csv_path}: {missing_cols}")
        raise ExtractDataError(f"Missing columns in {csv_path}: {missing_cols}")

    # Lettura di tutte le righe del file
    try:
        with open(csv_path, encoding="utf-8") as f:
            total_rows = max(sum(1 for _ in f) - 1, 0)
    except FileNotFoundError as e:
        log.error(f"[read_csv_metadata] File not found: {csv_path}")
        raise ExtractDataError(f"File not found: {csv_path}") from e
    except UnicodeDecodeError as e:
        log.error(f"[read_csv_metadata] Encoding error while reading file: {csv_path}")
        raise ExtractDataError(f"Encoding error while reading file: {csv_path}") from e
    except OSError as e:
        log.error(f"[read_csv_metadata] Error while reading file {csv_path}: {e}")
        raise ExtractDataError(f"Error while reading file {csv_path}: {e}") from e

    log.info(f"[read_csv_metadata] Total rows in {csv_path}: {total_rows}")

    return CsvMetadata(
        source_file=csv_path,
        available_columns=available_list_columns,
        selected_columns=required_columns,
        total_rows=total_rows
    )