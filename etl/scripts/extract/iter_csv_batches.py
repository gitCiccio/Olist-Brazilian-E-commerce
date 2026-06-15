"""
Lo script iter_csv_batches serve a leggere il CSV a pezzi in batch di dimensione fissa
senza fare pd.read_csv completo. Permettendo di mantenere l'uso di memoria più stabile
e si adatta bene a un'estrazione incrementale o restartable
"""
import pandas as pd
from pathlib import Path
from typing import Iterator

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError

log = AppLogger(name="iter_csv_batches.extract", log_file="iter_csv_batches.log")

def iter_csv_batches(csv_path: str, selected_columns: list[str], batch_size: int, start_row: int = 0) -> Iterator[pd.DataFrame]:
    log.info(f"[iter_csv_batches] Reading {csv_path} in batches of {batch_size} starting from row {start_row}")

    path = Path(csv_path)

    if not path.exists():
        log.error(f"[iter_csv_batches] File not found: {csv_path}")
        raise ExtractDataError(f"File not found: {csv_path}")

    if not path.is_file():
        log.error(f"[iter_csv_batches] Path is not a file: {csv_path}")
        raise ExtractDataError(f"Path is not a file: {csv_path}")

    if selected_columns is None:
        log.error(f"[iter_csv_batches] Selected columns is None for file: {csv_path}")
        raise ExtractDataError(f"Selected columns is None for file: {csv_path}")

    if batch_size <= 0:
        log.error(f"[iter_csv_batches] Batch size is not positive for file: {csv_path}")
        raise ExtractDataError(f"Batch size is not positive for file: {csv_path}")

    if start_row < 0:
        log.error(f"[iter_csv_batches] Start row is not positive for file: {csv_path}")
        raise ExtractDataError(f"Start row is not positive for file: {csv_path}")


    try:
        # Lettore pandas
        # skiprows=range(1, start_row + 1) if start_row > 0 else None salta le righe dei dati già elaborati
        # mantenendo l' header alla riga 0
        reader = pd.read_csv(
            csv_path,
            usecols=selected_columns,
            dtype=str,
            chunksize=batch_size,
            skiprows=range(1, start_row + 1) if start_row > 0 else None
        )

        for batch_number, chunk in enumerate(reader, start=1):
            log.info(
                f"[iter_csv_batches] Yielding batch {batch_number} with {len(chunk)} rows"
            )
            """
            yield è la parola chiave che trasforma una funzione normale in una generator function. 
            Una funzione con yield non si comporta come una funzione che fa un solo return finale: 
            ogni volta che arriva a yield, restituisce un valore e si ferma temporaneamente, 
            ricordandosi dove era arrivata.
            """
            yield chunk

    except FileNotFoundError as e:
        log.error(f"[iter_csv_batches] File not found: {csv_path}")
        raise ExtractDataError(f"File not found: {csv_path}") from e
    except UnicodeDecodeError as e:
        log.error(f"[iter_csv_batches] Encoding error while reading file: {csv_path}")
        raise ExtractDataError(f"Encoding error while reading file: {csv_path}") from e
    except Exception as e:
        log.error(f"[iter_csv_batches] Error while iterating batches from {csv_path}: {e}")
        raise ExtractDataError(f"Error while iterating batches from {csv_path}: {e}") from e