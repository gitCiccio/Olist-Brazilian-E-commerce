#!/usr/bin/env python3
"""Apply foreign key constraints SQL to the staging DB (olist_db) using psycopg2."""
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2


def main():
    load_dotenv()
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = int(os.getenv('POSTGRES_PORT', '5433'))
    staging_db = os.getenv('POSTGRES_DB', 'olist_db')

    project_root = Path(__file__).resolve().parents[1]
    sql_file = project_root / 'db' / 'add_foreign_keys.sql'

    if not sql_file.exists():
        print(f"SQL file not found: {sql_file}")
        return

    conn = psycopg2.connect(dbname=staging_db, user=user, password=password, host=host, port=port)
    try:
        with conn.cursor() as cur:
            sql = sql_file.read_text(encoding='utf-8')
            print(f"Applying foreign keys from {sql_file} to database {staging_db}...")
            cur.execute(sql)
        conn.commit()
        print("Foreign keys applied successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error applying foreign keys: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()

