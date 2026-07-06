#!/usr/bin/env python3
"""Ensure all product_category_name values from products exist in product_category_name_translation."""
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

    conn = psycopg2.connect(dbname=staging_db, user=user, password=password, host=host, port=port)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT product_category_name FROM public.products WHERE product_category_name IS NOT NULL")
            cats = [r[0] for r in cur.fetchall()]
            cur.execute('SELECT product_category_name FROM public.product_category_name_translation')
            existing = {r[0] for r in cur.fetchall()}

            missing = [c for c in cats if c not in existing]
            if not missing:
                print("No missing product categories.")
                return

            print(f"Inserting {len(missing)} missing product_category_name rows into product_category_name_translation...")
            for c in missing:
                cur.execute(
                    "INSERT INTO public.product_category_name_translation (product_category_name, product_category_name_english) VALUES (%s, %s)",
                    (c, None)
                )
        conn.commit()
        print("Inserted missing categories.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

