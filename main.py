from db import *
from etl.db import db_connection
from etl.extract import extract_csv, get_or_create_checkpoint
from logger.logger import AppLogger
from sources import SOURCES

log = AppLogger(name="main.extract", log_file="main.log")

if __name__ == "__main__":
    log.info("Init program")
    db = db_connection()

    with db as connection:
        for dimension, config in SOURCES.items():
            df = extract_csv(config["file"], config["columns"])
            checkpoint = get_or_create_checkpoint(connection, config["file"], len(df))
            log.info(f"{dimension}: {len(df)} rows, checkpoint at row {checkpoint['last_row_extracted']}")