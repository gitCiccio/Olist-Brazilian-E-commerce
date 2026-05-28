from sqlalchemy import text
from logger.logger import AppLogger
import pandas as pd

log = AppLogger(name="extract.extract", log_file="extract.log")
BATCH_SIZE = 1000


def _get_or_create_checkpoint(conn, source_file: str, total_rows: int) -> dict:
    log.info(f"[checkpoint] Source file: {source_file}")

    result = conn.execute(
        text("SELECT id, last_row_extracted FROM etl_checkpoint "
             "WHERE source_file = :sf "
             "AND status IN ('RUNNING', 'FAILED') "
             "ORDER BY started_at DESC LIMIT 1"),
        {"sf": source_file}
    ).mappings().first()

    if result:
        log.info(f"[checkpoint] Resuming {source_file} from row {result['last_row_extracted']}")
        return dict(result)

    result = conn.execute(
        text("INSERT INTO etl_checkpoint (source_file, last_row_extracted, total_rows, status) "
             "VALUES (:sf, 0, :tr, 'RUNNING') RETURNING id, last_row_extracted"),
        {"sf": source_file, "tr": total_rows}
    ).mappings().first()

    log.info(f"[checkpoint] Created new checkpoint for {source_file}")
    return dict(result)


def extract_and_stage(
    csv_path: str,
    columns: list[str],
    staging_table: str,
    engine,
    truncate: bool = False
) -> pd.DataFrame:

    df_full = pd.read_csv(csv_path, dtype=str)
    if columns:
        df_full = df_full[columns]
    total_rows = len(df_full)

    with engine.begin() as conn:
        if truncate:
            conn.execute(text(f"TRUNCATE TABLE staging.{staging_table}"))
            conn.execute(
                text("UPDATE etl_checkpoint SET status = 'FAILED', blocked_at = NOW() "
                     "WHERE source_file = :sf AND status IN ('RUNNING', 'COMPLETED')"),
                {"sf": csv_path}
            )
            log.info(f"[staging] Truncated staging.{staging_table} + reset checkpoint")

        checkpoint = _get_or_create_checkpoint(conn, csv_path, total_rows)
        start_row = checkpoint['last_row_extracted']
        checkpoint_id = checkpoint['id']

        log.info(f"[extract] Resuming {csv_path} from row {start_row}")

        df_to_process = df_full.iloc[start_row:]
        for i in range(0, len(df_to_process), BATCH_SIZE):
            batch = df_to_process.iloc[i:i + BATCH_SIZE]
            last_row = start_row + i + len(batch)

            batch.to_sql(
                name=staging_table,
                con=conn,
                schema='staging',
                if_exists='append',
                index=False,
                method='multi'
            )
            conn.execute(
                text("UPDATE etl_checkpoint "
                     "SET last_row_extracted = :row, last_committed_at = NOW() "
                     "WHERE id = :id"),
                {"row": last_row, "id": str(checkpoint_id)}
            )
            log.info(f"[extract] Batch {i // BATCH_SIZE + 1}: rows {start_row + i} → {last_row}")

        conn.execute(
            text("UPDATE etl_checkpoint SET status = 'COMPLETED', completed_at = NOW() "
                 "WHERE id = :id"),
            {"id": str(checkpoint_id)}
        )
        log.info(f"[extract] {csv_path} → staging.{staging_table} COMPLETED ({total_rows} rows)")

    return df_full