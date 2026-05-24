from pandas.core.ops import missing

from logger.logger import AppLogger
import pandas as pd

log = AppLogger(name="extract.extract", log_file="extract.log")
BATCH_SIZE = 1000

def get_or_create_checkpoint(db, source_file, total_rows) -> dict:
    log.info("Checkpoint creation")
    log.info(f"Source file: {source_file}")

    existing = db.execute(
        "SELECT * FROM etl_checkpoint WHERE source_file = %s"
        "AND status in ('RUNNING', 'FAILED') ORDER BY started_at DESC LIMIT 1",
        (source_file,)
    ).fetch_one()

    if existing:
        log.info(f"Resuming {source_file} from row {existing['last_row_extracted']}")
        return dict(existing)

    db.execute(
        "INSERT INTO etl_checkpoint (source_file, last_row_extracted, total_rows, status) VALUES (%s, 0, %s, 'RUNNING')",
        (source_file, total_rows)
    )
    db.commit()

    return db.execute(
        "SELECT * FROM etl_checkpoint WHERE source_file = %s ORDER BY started_at DESC LIMIT 1",
        (source_file,)
    ).fetch_one()

def extract_batches(csv_path: str, start_row: int):
    log.info(f"Extracting {start_row} rows from {csv_path}")
    df = pd.read_csv(csv_path, skiprows=range(1, start_row + 1))

    for i in range(0, len(df), BATCH_SIZE):
        batch = df.iloc[i : i + BATCH_SIZE]
        yield batch, start_row + i + len(batch)

def extract_csv(csv_path: str, columns: list[str] = None) -> pd.DataFrame:
    log.info(f"Extracting {columns} from {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)

    if columns:
        missing = [column for column in columns if column not in df.columns]
        if missing:
            log.error(f"Missing columns: {missing}")
            raise ValueError(f"Columns not found in {csv_path}: {missing}")
        df = df[columns]

    log.info(f"Extracted {len(df)} rows, {len(df.columns)} columns from {csv_path}")
    return df