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
            schema='public',
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000

        )

    log.info(f"[load] dim_seller: {len(dt_sellers_copy)} rows loaded")

def load_dim_customers(df_customers: pd.DataFrame, engine) -> None:
    df_customers_copy = df_customers.copy()

    with engine.begin() as connection:
        df_customers_copy.to_sql(
            name='dim_customer',
            con=connection,
            schema='public',
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000

        )

    log.info(f"[load] dim_customer: {len(df_customers_copy)} rows loaded")

def load_dim_product(df_product: pd.DataFrame, engine) -> None:
    df_product_copy = df_product.copy()

    with engine.begin() as connection:
        df_product_copy.to_sql(
            name='dim_product',
            con=connection,
            schema='public',
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000

        )

    log.info(f"[load] dim_product: {len(df_product_copy)} rows loaded")

def load_dim_payment(df_payment: pd.DataFrame, engine) -> None:
    df_payment_copy = df_payment.copy()

    with engine.begin() as connection:
        df_payment_copy.to_sql(
            name='dim_payment',
            con=connection,
            schema='public',
            if_exists='append',
            index=False,
            method='multi',
            chunksize= 1000
        )

    log.info(f"[load] dim_payment: {len(df_payment_copy)} rows loaded")

def load_dim_date(df_date: pd.DataFrame, engine) -> tuple[int, pd.DataFrame]:
    """
    Carica dim_date con upsert (INSERT ... ON CONFLICT) per evitare duplicati.
    Restituisce (num_rows_loaded, date_mapping).
    """
    df_date_copy = df_date.copy()

    with engine.connect() as conn:
        # 1. Controlla quante date esistono già
        existing = pd.read_sql(
            "SELECT natural_key, surrogate_key, full_date FROM public.dim_date",
            conn
        )

    if not existing.empty:
        # 2. Filtra solo le date non già presenti
        df_new = df_date_copy[
            ~df_date_copy['natural_key'].isin(existing['natural_key'])
        ].copy()
        log.info(f"[load] dim_date: {len(existing)} date già presenti, "
                 f"{len(df_new)} nuove da inserire")
    else:
        df_new = df_date_copy.copy()
        log.info(f"[load] dim_date: {len(df_new)} nuove date da inserire")

    if df_new.empty:
        log.info("[load] dim_date: nessuna nuova data da caricare")
        return 0, existing

    # 3. Carica le nuove righe
    with engine.begin() as conn:
        df_new.to_sql(
            name='dim_date',
            con=conn,
            schema='public',
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )

    # 4. Reload complete mapping
    with engine.connect() as conn:
        date_mapping = pd.read_sql(
            "SELECT surrogate_key, full_date FROM public.dim_date",
            conn
        )

    log.info(f"[load] dim_date: {len(df_new)} righe caricate, "
             f"totale {len(date_mapping)} righe in tabella")
    return len(df_new), date_mapping


def load_fact_table(
    df_fact: pd.DataFrame,
    date_mapping: pd.DataFrame,
    engine,
) -> None:
    df = df_fact.copy()

    # --- Passo 1: full_date → date_id ---
    date_mapping = date_mapping.copy()
    if date_mapping['full_date'].dtype == 'datetime64[ns]':
        date_mapping['full_date'] = date_mapping['full_date'].dt.date
    df['full_date'] = pd.to_datetime(df['full_date']).dt.date

    df = df.merge(date_mapping, on='full_date', how='left').rename(
        columns={'surrogate_key': 'date_id'}
    )

    # --- Passo 2: payment_type → payment_id (surrogate_key) ---
    with engine.connect() as conn:
        payment_map = pd.read_sql(
            "SELECT surrogate_key, payment_type FROM public.dim_payment",
            conn
        )
    df = df.merge(
        payment_map.rename(columns={'surrogate_key': 'payment_id'}),
        on='payment_type',
        how='left'
    )

    # --- Passo 3: customer_id → customer_id (surrogate_key) ---
    with engine.connect() as conn:
        customer_map = pd.read_sql(
            "SELECT surrogate_key, natural_key FROM public.dim_customer",
            conn
        )
    df = df.merge(
        customer_map.rename(columns={'surrogate_key': 'customer_id_fk'})
                    .rename(columns={'natural_key': 'customer_id_nat'}),
        left_on='customer_id',
        right_on='customer_id_nat',
        how='left'
    )

    # --- Passo 4: seller_id → seller_id (surrogate_key) ---
    with engine.connect() as conn:
        seller_map = pd.read_sql(
            "SELECT surrogate_key, natural_key FROM public.dim_seller",
            conn
        )
    df = df.merge(
        seller_map.rename(columns={'surrogate_key': 'seller_id_fk'})
                  .rename(columns={'natural_key': 'seller_id_nat'}),
        left_on='seller_id',
        right_on='seller_id_nat',
        how='left'
    )

    # --- Passo 5: product_id → product_id (surrogate_key) ---
    with engine.connect() as conn:
        product_map = pd.read_sql(
            "SELECT surrogate_key, natural_key FROM public.dim_product",
            conn
        )
    df = df.merge(
        product_map.rename(columns={'surrogate_key': 'product_id_fk'})
                   .rename(columns={'natural_key': 'product_id_nat'}),
        left_on='product_id',
        right_on='product_id_nat',
        how='left'
    )

    # --- Passo 6: verifica FK ---
    for fk in ['date_id', 'payment_id', 'customer_id_fk', 'seller_id_fk', 'product_id_fk']:
        null_count = df[fk].isna().sum()
        if null_count > 0:
            log.warning(f"[load] fact_sell: {null_count} righe senza {fk} → escluse")
            df = df.dropna(subset=[fk])

    # --- Passo 7: seleziona e rinomina per il DDL ---
    df = df[[
        'natural_key',
        'order_item_id',
        'price',
        'freight_value',
        'payment_value',
        'review_score',
        'delivery_days',
        'product_id_fk',
        'date_id',
        'payment_id',
        'customer_id_fk',
        'seller_id_fk'
    ]].rename(columns={
        'product_id_fk': 'product_id',
        'customer_id_fk': 'customer_id',
        'seller_id_fk': 'seller_id'
    })

    with engine.begin() as connection:
        df.to_sql(
            name='fact_sell',
            con=connection,
            schema='public',
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )

    log.info(f"[load] fact_sell: {len(df)} rows loaded")