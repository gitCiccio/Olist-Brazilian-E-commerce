import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv


def list_tables(database_url, schema=None):
    print(f"Connecting to: {database_url}")
    engine = create_engine(database_url)
    inspector = inspect(engine)
    try:
        with engine.connect() as conn:
            if schema:
                tables = inspector.get_table_names(schema=schema)
                print(f"Tables in schema '{schema}': {tables}\n")
            else:
                tables = inspector.get_table_names()
                print(f"Tables: {tables}\n")
    except Exception as e:
        print(f"ERROR connecting to {database_url}: {e}\n")


if __name__ == '__main__':
    load_dotenv()

    # Prefer DATABASE_URL if present, otherwise build from .env values
    db_url_star = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg2://postgres:Postgres123:_@localhost:5433/olist_star_schema'
    )

    # Derive olist_db URL (staging) from .env POSTGRES_DB if different
    post_db = os.getenv('POSTGRES_DB', 'olist_db')
    # build staging DB URL pointing to olist_db on the same host/port
    # assume same credentials as DATABASE_URL or .env
    user = os.getenv('POSTGRES_USER', 'postgres')
    pwd = os.getenv('POSTGRES_PASSWORD', 'Postgres123:_')
    host = 'localhost'
    port = os.getenv('POSTGRES_PORT', '5433')

    db_url_staging = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{post_db}"

    print('\n--- TEST: star schema database ---')
    list_tables(db_url_star, schema='public')

    print('--- TEST: staging database ---')
    list_tables(db_url_staging, schema='staging')

