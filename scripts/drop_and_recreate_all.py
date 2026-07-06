#!/usr/bin/env python3
"""Drop staging and star databases and recreate them from scratch, then reload data.

Steps:
- connect to postgres database as admin
- terminate connections to target DBs
- drop databases if exist
- create databases
- run scripts/recreate_and_load_db.py to create tables and load CSVs
- ensure product categories and apply foreign keys
- run main.py to execute ETL
"""
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2


def terminate_and_drop(cur, dbname: str):
    # terminate connections
    cur.execute("SELECT pid FROM pg_stat_activity WHERE datname=%s AND pid<>pg_backend_pid()", (dbname,))
    pids = [r[0] for r in cur.fetchall()]
    for pid in pids:
        try:
            cur.execute("SELECT pg_terminate_backend(%s)", (pid,))
        except Exception:
            pass
    cur.execute(f"DROP DATABASE IF EXISTS \"{dbname}\"")


def create_db(cur, dbname: str):
    cur.execute(f"CREATE DATABASE \"{dbname}\"")


def main():
    load_dotenv()
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = int(os.getenv('POSTGRES_PORT', '5433'))
    staging_db = os.getenv('POSTGRES_DB', 'olist_db')

    database_url = os.getenv('DATABASE_URL')
    if database_url and '/' in database_url.rstrip('/'):
        star_db = database_url.rstrip('/').split('/')[-1]
    else:
        star_db = 'olist_star_schema'

    project_root = Path(__file__).resolve().parents[1]

    print(f"Dropping and recreating databases: {staging_db}, {star_db} on {host}:{port}")

    conn = psycopg2.connect(dbname='postgres', user=user, password=password, host=host, port=port)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            # drop/create staging DB
            terminate_and_drop(cur, staging_db)
            print(f"Dropped database {staging_db}")
            create_db(cur, staging_db)
            print(f"Created database {staging_db}")

            # drop/create star DB
            terminate_and_drop(cur, star_db)
            print(f"Dropped database {star_db}")
            create_db(cur, star_db)
            print(f"Created database {star_db}")
    finally:
        conn.close()

    # Run recreate_and_load_db.py to create tables and load CSVs
    print("Running recreate_and_load_db.py to create schemas/tables and load CSVs...")
    # use the same python interpreter that's running this script
    python_exec = sys.executable
    subprocess.run([python_exec, str(project_root / 'scripts' / 'recreate_and_load_db.py')], check=True)

    # Ensure categories and apply foreign keys
    print("Ensuring product categories exist...")
    subprocess.run([python_exec, str(project_root / 'scripts' / 'ensure_product_categories.py')], check=True)

    print("Applying foreign keys...")
    subprocess.run([python_exec, str(project_root / 'scripts' / 'apply_foreign_keys.py')], check=True)

    # Run main ETL to populate star schema
    print("Running main ETL script (main.py)...")
    subprocess.run([python_exec, str(project_root / 'main.py')], check=True)

    print("Drop and recreate completed successfully.")


if __name__ == '__main__':
    main()

