#!/usr/bin/env python3
"""Ricrea gli schemi/tabelle e carica i CSV nel database usando psycopg2.

Questo script:
- legge le variabili da .env
- crea il database star se non esiste
- esegue gli SQL in db/create_raw_tables.sql e db/staging_area.sql sul DB di staging (POSTGRES_DB)
- esegue gli SQL in db/create_star_schema.sql sul database star (rimuovendo la riga psql "\\c ...")
- carica i CSV presenti in data/raw nelle tabelle public del DB di staging usando COPY

Usalo dalla root del progetto con l'ambiente virtuale attivato:
  python .\scripts\recreate_and_load_db.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
import pandas as pd
from io import StringIO


def read_sql(path: Path) -> str:
    text = path.read_text(encoding='utf-8')
    return text


def exec_sql(conn, sql: str):
    with conn.cursor() as cur:
        try:
            cur.execute(sql)
        except psycopg2.errors.DuplicateTable as e:
            # Some SQL files may try to create objects that already exist - ignore
            print(f"Warning: object already exists (ignored): {e}")
            conn.rollback()
            return
        except Exception:
            # re-raise any other error after rolling back
            conn.rollback()
            raise
    conn.commit()


def exec_sql_file(conn, path: Path, strip_psql_meta: bool = False):
    text = read_sql(path)
    if strip_psql_meta:
        # remove psql meta-commands like \c ...
        lines = [l for l in text.splitlines() if not l.strip().startswith('\\c')]
        text = '\n'.join(lines)
    exec_sql(conn, text)


def load_csv_to_table(conn, table: str, file_path: Path):
    """Load CSV into table but drop duplicate PKs in the CSV before COPY.

    Uses pandas to remove duplicates (based on known primary key mapping) and
    then performs COPY FROM STDIN from an in-memory buffer.
    """
    print(f"Loading {file_path} -> {table}")

    # primary key mapping for raw tables (used to drop duplicate rows in CSV)
    pk_map = {
        'customers': ['customer_id'],
        'sellers': ['seller_id'],
        'products': ['product_id'],
        'product_category_name_translation': ['product_category_name'],
        'orders': ['order_id'],
        'order_items': ['order_id', 'order_item_id'],
        'order_payments': ['order_id', 'payment_sequential'],
        'order_reviews': ['review_id']
    }

    # read with pandas to drop duplicates if needed
    df = pd.read_csv(file_path, dtype=str)
    pk = pk_map.get(table)
    if pk:
        # drop rows with duplicated PK (keep first)
        existing_rows = len(df)
        df = df.drop_duplicates(subset=pk, keep='first')
        dropped = existing_rows - len(df)
        if dropped:
            print(f"Dropped {dropped} duplicate rows based on PK {pk}")
    else:
        # drop exact duplicate rows
        existing_rows = len(df)
        df = df.drop_duplicates(keep='first')
        dropped = existing_rows - len(df)
        if dropped:
            print(f"Dropped {dropped} exact duplicate rows")

    # copy from in-memory CSV
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=True)
    buffer.seek(0)
    with conn.cursor() as cur:
        sql = f"COPY {table} FROM STDIN WITH CSV HEADER"
        cur.copy_expert(sql, buffer)
    conn.commit()


def main():
    load_dotenv()
    project_root = Path(__file__).resolve().parents[1]
    db_dir = project_root / 'db'
    data_dir = project_root / 'data' / 'raw'

    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = int(os.getenv('POSTGRES_PORT', '5433'))

    # NEW: Separate databases for each layer
    staging_db = os.getenv('POSTGRES_STAGING_DB', 'olist_staging')
    reconciled_db = os.getenv('POSTGRES_RECONCILED_DB', 'olist_reconciled')
    dw_db = os.getenv('POSTGRES_DW_DB', 'olist_dw')

    print(f"User: {user}, host: {host}, port: {port}")
    print(f"Staging DB: {staging_db}")
    print(f"Reconciled DB: {reconciled_db}")
    print(f"DW DB: {dw_db}")

    # NOTE: Databases should already exist (created via Docker SQL commands)
    # This script only populates them.

    # === STAGING LAYER ===
    # Execute SQL to create raw tables on staging_db
    conn_staging = psycopg2.connect(dbname=staging_db, user=user, password=password, host=host, port=port)
    try:
        print("\n[STAGING] Executing create_raw_tables.sql...")
        exec_sql_file(conn_staging, db_dir / 'create_raw_tables.sql')

        # Load CSV files into staging public tables
        files = [
            ('customers', 'olist_customers_dataset.csv'),
            ('sellers', 'olist_sellers_dataset.csv'),
            ('products', 'olist_products_dataset.csv'),
            ('product_category_name_translation', 'product_category_name_translation.csv'),
            ('geolocation', 'olist_geolocation_dataset.csv'),
            ('orders', 'olist_orders_dataset.csv'),
            ('order_items', 'olist_order_items_dataset.csv'),
            ('order_payments', 'olist_order_payments_dataset.csv'),
            ('order_reviews', 'olist_order_reviews_dataset.csv'),
        ]

        print("[STAGING] Loading CSV files...")
        for table, fname in files:
            fpath = data_dir / fname
            if not fpath.exists():
                print(f"Warning: file not found {fpath}, skipping")
                continue
            # clean table before loading so script can be re-run safely
            with conn_staging.cursor() as cur:
                try:
                    cur.execute(f'TRUNCATE TABLE public."{table}" CASCADE')
                    conn_staging.commit()
                    print(f"  Truncated public.{table}")
                except Exception as e:
                    conn_staging.rollback()
                    print(f"  Warning: could not truncate public.{table}: {e}")
            load_csv_to_table(conn_staging, table, fpath)

    finally:
        conn_staging.close()

    # === RECONCILED LAYER ===
    # Create reconciled schema and tables (will be populated by transform phase)
    conn_reconciled = psycopg2.connect(dbname=reconciled_db, user=user, password=password, host=host, port=port)
    try:
        print("\n[RECONCILED] Executing reconciled_layer.sql...")
        exec_sql_file(conn_reconciled, db_dir / 'reconciled_layer.sql')
    finally:
        conn_reconciled.close()

    # === DATA WAREHOUSE LAYER ===
    # Create DW schema with dim_*, fact_*, etl_checkpoint (will be populated by DW load phase)
    conn_dw = psycopg2.connect(dbname=dw_db, user=user, password=password, host=host, port=port)
    try:
        print("\n[DW] Executing create_star_schema.sql...")
        # Remove psql meta-commands (e.g., \c olist_star_schema)
        text = read_sql(db_dir / 'create_star_schema.sql')
        lines = [l for l in text.splitlines() if not l.strip().startswith('\\c')]
        text = '\n'.join(lines)
        exec_sql(conn_dw, text)
    finally:
        conn_dw.close()

    print("\n✓ Database initialization complete (staging + reconciled + DW schemas created).")


if __name__ == '__main__':
    main()

