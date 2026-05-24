import pandas as pd

from db import *
from etl.db import db_connection
from etl.extract import extract_csv, get_or_create_checkpoint
from etl.trasform import transform_dim_sellers, transform_dim_payment, transform_dim_customers, transform_dim_date
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

    """# Test
    df_sellers = pd.read_csv(SOURCES["dim_seller"]["file"])
    seller_cities = df["seller_city"].unique().tolist()
    seller_states = df["seller_state"].unique().tolist()
    print(seller_cities)
    print(seller_states)

    df_customers = pd.read_csv(SOURCES["dim_customer"]["file"])
    customer_cities = df["customer_city"].unique().tolist()
    customer_states = df["customer_state"].unique().tolist()
    print(customer_cities)
    print(customer_states)
"""

    df_payment = extract_csv(SOURCES["dim_payment"]["file"])
    transform_dim_payment(df_payment)

    df_sellers = extract_csv(SOURCES["dim_seller"]["file"])
    transform_dim_sellers(df_sellers)

    df_customers = extract_csv(SOURCES["dim_customer"]["file"])
    transform_dim_customers(df_customers)

    df_date = extract_csv(SOURCES["dim_date"]["file"])
    transform_dim_date(df_date)

    df_product = extract_csv(SOURCES["dim_product"]["file"])
    # transform_dim_product(df_product)