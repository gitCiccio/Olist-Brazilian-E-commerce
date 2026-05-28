from typing import Iterator

import pandas as pd
from pandas import DataFrame

from logger.logger import AppLogger

log = AppLogger(name="load.extract", log_file="load.log")


def load_dim_sellers(df_sellers: pd.DataFrame, engine) -> None:
    dt_sellers_copy = df_sellers.copy()

    with engine.begin() as connection:
        dt_sellers_copy.to_sql(
            name='dim_seller',
            con=connection,
            schema='olist_star_schema',
            if_exists='append',
            index=False,
            method='multi',
        )

    log.info(f"[load] dim_seller: {len(dt_sellers_copy)} rows loaded")

def load_dim_customers(df_customers: pd.DataFrame, engine) -> None:
    df_customers_copy = df_customers.copy()

    with engine.begin() as connection:
        df_customers_copy.to_sql(
            name='dim_customer',
            con=connection,
            schema='olist_star_schema',
            if_exists='append',
            index=False,
            method='multi',
        )

    log.info(f"[load] dim_customer: {len(df_customers_copy)} rows loaded")

def load_dim_product(df_product: pd.DataFrame, engine) -> None:
    df_product_copy = df_product.copy()

    with engine.begin() as connection:
        df_product_copy.to_sql(
            name='dim_product',
            con=connection,
            schema='olist_star_schema',
            if_exists='append',
            index=False,
            method='multi',
        )

    log.info(f"[load] dim_product: {len(df_product_copy)} rows loaded")

def load_dim_payment(df_payment: pd.DataFrame, engine) -> None:
    df_payment_copy = df_payment.copy()

    with engine.begin() as connection:
        df_payment_copy.to_sql(
            name='dim_payment',
            con=connection,
            schema='olist_star_schema',
            if_exists='append',
            index=False,
            method='multi',
        )

    log.info(f"[load] dim_payment: {len(df_payment_copy)} rows loaded")

def load_dim_date(df_date: pd.DataFrame, engine) -> DataFrame | Iterator[DataFrame]:
    df_date_copy = df_date.copy()

    df_date_copy = df_date_copy.drop(columns=['natural_key'])

    with engine.begin() as connection:
        df_date_copy.to_sql(
            name='dim_date',
            con=connection,
            schema='olist_star_schema',
            if_exists='append',
            index=False,
            method='multi'
        )

    with engine.connect() as connection:
        date_mapping = pd.read_sql(
            "SELECT date_id, full_date FROM olist_star_schema.dim_date",
            connection
        )

    log.info(f"[load] dim_date: {len(df_date_copy)} rows loaded")
    return date_mapping

def load_fact_table(
        df_fact: pd.DataFrame,
        df_dim_date: pd.DataFrame,   # natural_key(=order_id), full_date
        date_mapping: pd.DataFrame,
        engine,
) -> None:
    df = df_fact.copy()

    # Passo 1: order_id → full_date
    df = df.merge(
        df_dim_date.rename(columns={'natural_key': 'order_id'})[['order_id', 'full_date']],
        on='order_id',
        how='left'
    )

    # Passo 2: full_date → date_id
    date_mapping['full_date'] = pd.to_datetime(date_mapping['full_date']).dt.date
    df['full_date'] = pd.to_datetime(df['full_date']).dt.date

    df = df.merge(date_mapping, on='full_date', how='left')

    # Passo 3: verifica FK — quanti order_id non hanno date_id?
    null_date_id = df['date_id'].isna().sum()
    if null_date_id > 0:
        log.warning(f"[load] fact_vendita: {null_date_id} righe senza date_id → escluse")
        df = df.dropna(subset=['date_id'])

    # Passo 4: seleziona solo le colonne della tabella DW
    df = df[[
        'order_id',
        'order_item_id',
        'date_id',
        'product_id',
        'customer_id',
        'seller_id',
        'payment_type',
        'price',
        'freight_value',
        'payment_value',
        'review_score',
        'delivery_days'
    ]]

    with engine.begin() as connection:
        df.to_sql(
            name='fact_vendita',
            con=connection,
            schema='olist_star_schema',
            if_exists='append',
            index=False,
            method='multi'
        )

    log.info(f"[load] fact_vendita: {len(df)} rows loaded")