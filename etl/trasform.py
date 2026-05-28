from typing import Any

import numpy as np
import pandas as pd
from unidecode import unidecode
from logger.logger import AppLogger

log = AppLogger(name="transform.extract", log_file="transform.log")


# Fase one: conversion & normalization
# Tipi validi
VALID_PAYMENT_TYPES = {'credit_card', 'boleto', 'voucher', 'debit_card', 'not_defined'}
# Mapping
PAYMENT_MAPPING = {'boleto': 'ticket'}
CATEGORY_TRANSLATION = {
    "beleza_saude": "health_beauty",
    "informatica_acessorios": "computers_accessories",
    "automotivo": "auto",
    "cama_mesa_banho": "bed_bath_table",
    "moveis_decoracao": "furniture_decor",
    "esporte_lazer": "sports_leisure",
    "perfumaria": "perfumery",
    "utilidades_domesticas": "housewares",
    "telefonia": "telephony",
    "relogios_presentes": "watches_gifts",
    "alimentos_bebidas": "food_drink",
    "bebes": "baby",
    "papelaria": "stationery",
    "tablets_impressao_imagem": "tablets_printing_image",
    "brinquedos": "toys",
    "telefonia_fixa": "fixed_telephony",
    "ferramentas_jardim": "garden_tools",
    "fashion_bolsas_e_acessorios": "fashion_bags_accessories",
    "eletroportateis": "small_appliances",
    "consoles_games": "consoles_games",
    "audio": "audio",
    "fashion_calcados": "fashion_shoes",
    "cool_stuff": "cool_stuff",
    "malas_acessorios": "luggage_accessories",
    "climatizacao": "air_conditioning",
    "construcao_ferramentas_construcao": "construction_tools_construction",
    "moveis_cozinha_area_de_servico_jantar_e_jardim": "kitchen_dining_laundry_garden_furniture",
    "construcao_ferramentas_jardim": "costruction_tools_garden",
    "fashion_roupa_masculina": "fashion_male_clothing",
    "pet_shop": "pet_shop",
    "moveis_escritorio": "office_furniture",
    "market_place": "market_place",
    "eletronicos": "electronics",
    "eletrodomesticos": "home_appliances",
    "artigos_de_festas": "party_supplies",
    "casa_conforto": "home_confort",
    "construcao_ferramentas_ferramentas": "costruction_tools_tools",
    "agro_industria_e_comercio": "agro_industry_and_commerce",
    "moveis_colchao_e_estofado": "furniture_mattress_and_upholstery",
    "livros_tecnicos": "books_technical",
    "casa_construcao": "home_construction",
    "instrumentos_musicais": "musical_instruments",
    "moveis_sala": "furniture_living_room",
    "construcao_ferramentas_iluminacao": "construction_tools_lights",
    "industria_comercio_e_negocios": "industry_commerce_and_business",
    "alimentos": "food",
    "artes": "art",
    "moveis_quarto": "furniture_bedroom",
    "livros_interesse_geral": "books_general_interest",
    "construcao_ferramentas_seguranca": "construction_tools_safety",
    "fashion_underwear_e_moda_praia": "fashion_underwear_beach",
    "fashion_esporte": "fashion_sport",
    "sinalizacao_e_seguranca": "signaling_and_security",
    "pcs": "computers",
    "artigos_de_natal": "christmas_supplies",
    "fashion_roupa_feminina": "fashio_female_clothing",
    "eletrodomesticos_2": "home_appliances_2",
    "livros_importados": "books_imported",
    "bebidas": "drinks",
    "cine_foto": "cine_photo",
    "la_cuisine": "la_cuisine",
    "musica": "music",
    "casa_conforto_2": "home_comfort_2",
    "portateis_casa_forno_e_cafe": "small_appliances_home_oven_and_coffee",
    "cds_dvds_musicais": "cds_dvds_musicals",
    "dvds_blu_ray": "dvds_blu_ray",
    "flores": "flowers",
    "artes_e_artesanato": "arts_and_craftmanship",
    "fraldas_higiene": "diapers_and_hygiene",
    "fashion_roupa_infanto_juvenil": "fashion_childrens_clothes",
    "seguros_e_servicos": "security_and_services",
}
# Regex
STATE_REGEX = (r'^[A-Z]{2}$')


def transform_dim_payment(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    payment_data_frame_copy = df.copy()
    total_input = len(payment_data_frame_copy)

    # --- Cast prima di tutto ---
    payment_data_frame_copy['payment_value'] = pd.to_numeric(
        payment_data_frame_copy['payment_value'], errors='coerce'
    )
    payment_data_frame_copy['payment_type'] = payment_data_frame_copy['payment_type'].str.strip().str.lower()

    # --- Cleansing payment_type ---
    null_type_count = payment_data_frame_copy['payment_type'].isnull().sum()
    if null_type_count > 0:
        payment_data_frame_copy['payment_type'] = payment_data_frame_copy['payment_type'].fillna('not_defined')

    payment_data_frame_copy['payment_type'] = payment_data_frame_copy['payment_type'].replace(PAYMENT_MAPPING)

    invalid_mask = ~payment_data_frame_copy['payment_type'].isin(VALID_PAYMENT_TYPES)
    if invalid_mask.any():
        payment_data_frame_copy.loc[invalid_mask, 'payment_type'] = 'not_defined'

    # --- Cleansing payment_value ---
    null_value_count = payment_data_frame_copy['payment_value'].isna().sum()
    if null_value_count > 0:
        log.warning(f"[payment] {null_value_count} null payment_value → 0")
        payment_data_frame_copy['payment_value'] = payment_data_frame_copy['payment_value'].fillna(0)

    negative_mask = payment_data_frame_copy['payment_value'] < 0
    negative_count = negative_mask.sum()
    if negative_count > 0:
        log.warning(f"[payment] {negative_count} negative payment_value → 0")
        payment_data_frame_copy.loc[negative_mask, 'payment_value'] = 0

    # --- DIM: tipi unici ---
    dim = pd.DataFrame({'payment_type': sorted(payment_data_frame_copy['payment_type'].unique())})

    # --- FACT LOOKUP type: order_id → tipo dominante ---
    fact_lookup_type = (
        payment_data_frame_copy.groupby('order_id')['payment_type']
        .agg(lambda x: x.value_counts().idxmax())
        .reset_index()
        .rename(columns={'order_id': 'natural_key'})
    )

    # --- FACT LOOKUP value: order_id → somma pagamenti ---
    fact_lookup_value = (
        payment_data_frame_copy.groupby('order_id')['payment_value']
        .sum()
        .reset_index()
        .rename(columns={'order_id': 'natural_key'})
    )

    log.info(f"---------- quality report dim_payment ----------")
    log.info(f"[dim_payment] Input rows       : {total_input}")
    log.info(f"[dim_payment] Null types       : {null_type_count}")
    log.info(f"[dim_payment] Null values      : {null_value_count}")
    log.info(f"[dim_payment] Negative values  : {negative_count}")
    log.info(f"[dim_payment] DIM types        : {dim['payment_type'].tolist()}")
    log.info(f"[dim_payment] Unique order_id  : {fact_lookup_type['natural_key'].nunique()}")

    # da verificare se le info tra gli id combaciano
    return dim, fact_lookup_type, fact_lookup_value

def transform_dim_sellers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    before_dedup = total_input = len(df)

    df['seller_city'] = df['seller_city'].str.strip().str.lower().apply(unidecode)
    df['seller_state'] = df['seller_state'].str.strip().str.upper()
    invalid_mask = ~df['seller_state'].str.match(STATE_REGEX)

    if invalid_mask.any():
        log.warning(f"[dim_seller] {invalid_mask.sum()} invalid states → 'XX'")
        df.loc[invalid_mask, 'seller_state'] = 'XX'

    df = df.drop_duplicates(subset=['seller_id'], keep='first')
    after_dedup = len(df)

    log.info(f"---------- quality report dim_sellers ----------")
    log.info(f"[dim_seller] Input rows       : {total_input}")
    log.info(f"[dim_seller] Unique seller_id : {df['seller_id'].nunique()}")
    log.info(f"[dim_seller] Deduplicated     : {before_dedup} → {after_dedup} rows "
             f"({before_dedup - after_dedup} duplicates removed)")
    log.info(f"[dim_seller] States           : {df['seller_state'].value_counts().to_dict()}")
    log.info(f"[dim_seller] Cities           : {df['seller_city'].value_counts().to_dict()}")

    df = df.rename(columns={'seller_id': 'natural_key'})
    return df[['natural_key', 'seller_city', 'seller_state']]

def transform_dim_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    before_dedup = total_input = len(df)

    df['customer_city'] = df['customer_city'].str.strip().str.lower().apply(unidecode)
    df['customer_state'] = df['customer_state'].str.strip().str.upper()
    invalid_mask = ~df['customer_state'].str.match(STATE_REGEX)

    if invalid_mask.any():
        log.warning(f"[dim_customer] {invalid_mask.sum()} invalid states → 'XX'")
        df.loc[invalid_mask, 'customer_state'] = 'XX'

    df = df.drop_duplicates(subset=['customer_id'], keep='first')
    after_dedup = len(df)

    log.info(f"---------- quality report dim_customer ----------")
    log.info(f"[dim_customer] Input rows       : {total_input}")
    log.info(f"[dim_customer] Unique dim_customer : {df['customer_unique_id'].nunique()}")
    log.info(f"[dim_customer] Deduplicated     : {before_dedup} → {after_dedup} rows "
             f"({before_dedup - after_dedup} duplicates removed)")
    log.info(f"[dim_customer] States           : {df['customer_state'].value_counts().to_dict()}")
    log.info(f"[dim_customer] Cities           : {df['customer_city'].value_counts().to_dict()}")

    df = df.rename(columns={'customer_id': 'natural_key'})
    return df[['natural_key', 'customer_unique_id', 'customer_city', 'customer_state']]

def transform_dim_date(df: pd.DataFrame) -> tuple[Any, Any, Any]:
    df = df.copy()
    before_dedup = total_input = len(df)

    # --- order_purchase_timestamp ---
    df['order_purchase_timestamp'] = pd.to_datetime(
        df['order_purchase_timestamp'], errors='coerce'
    )
    nat_count = df['order_purchase_timestamp'].isna().sum()
    if nat_count > 0:
        log.warning(f"[dim_date] {nat_count} invalid timestamps → sentinel 1900-01-01")
        df['order_purchase_timestamp'] = df['order_purchase_timestamp'].fillna(
            pd.Timestamp('1900-01-01')
        )

    # --- order_delivered_customer_date ---
    df['order_delivered_customer_date'] = pd.to_datetime(
        df['order_delivered_customer_date'], errors='coerce'
    )
    nat_delivered_count = df['order_delivered_customer_date'].isna().sum()
    if nat_delivered_count > 0:
        log.warning(f"[dim_date] {nat_delivered_count} null delivery dates (ordini non consegnati)")

    # --- delivery_days: calcola PRIMA dei check ---
    df['delivery_days'] = (
        df['order_delivered_customer_date'] - df['order_purchase_timestamp']
    ).dt.days

    negative_mask = df['delivery_days'] < 0
    if negative_mask.any():
        log.warning(f"[dim_date] {negative_mask.sum()} negative delivery_days → NaN")
        df.loc[negative_mask, 'delivery_days'] = np.nan

    null_delivery_count = df['delivery_days'].isna().sum()
    log.warning(f"[dim_date] {null_delivery_count} null delivery_days (ordini non consegnati)")

    # --- Componenti data ---
    df['full_date'] = df['order_purchase_timestamp'].dt.date
    df['day']       = df['order_purchase_timestamp'].dt.day.astype('int16')
    df['month']     = df['order_purchase_timestamp'].dt.month.astype('int16')
    df['quarter']   = df['order_purchase_timestamp'].dt.quarter.astype('int16')
    df['year']      = df['order_purchase_timestamp'].dt.year.astype('int16')

    # --- Deduplicazione ---
    df = df.drop_duplicates(subset=['order_id'], keep='first')
    after_dedup = len(df)

    log.info(f"---------- quality report dim_date ----------")
    log.info(f"[dim_date] Input rows        : {total_input}")
    log.info(f"[dim_date] Unique order_id   : {df['order_id'].nunique()}")
    log.info(f"[dim_date] Deduplicated      : {before_dedup} → {after_dedup} rows "
             f"({before_dedup - after_dedup} duplicates removed)")
    log.info(f"[dim_date] Null delivered    : {nat_delivered_count}")
    log.info(f"[dim_date] Null delivery_days: {null_delivery_count}")
    log.info(f"[dim_date] Year distribution : {df['year'].value_counts().sort_index().to_dict()}")

    df = df.rename(columns={'order_id': 'natural_key'})
    return (
        df[['natural_key', 'full_date', 'day', 'month', 'quarter', 'year']],
        df[['natural_key', 'customer_id']],
        df[['natural_key', 'delivery_days']]
    )
# valori mancanti -> without_category
def transform_dim_product(df_product: pd.DataFrame) -> pd.DataFrame:
    df_product = df_product.copy()
    before_dedup = total_input = len(df_product)

    # Valori mancanti → sentinella PT che il mapping traduce
    null_count = df_product['product_category_name'].isna().sum()
    if null_count > 0:
        log.warning(f"[dim_product] {null_count} null categories → 'sem_categoria'")
        df_product['product_category_name'] = df_product['product_category_name'].fillna('sem_categoria')

    # Normalizzazione formato
    df_product['product_category_name'] = df_product['product_category_name'].str.strip().str.lower()

    # Mantieni PT, crea EN tramite mapping
    df_product['category_name_pt'] = df_product['product_category_name']
    df_product['category_name_en'] = df_product['product_category_name'].map(CATEGORY_TRANSLATION)

    # Fallback per categorie non nel dizionario
    not_found_mask = df_product['category_name_en'].isna()
    if not_found_mask.any():
        log.warning(f"[dim_product] {not_found_mask.sum()} categories not in dictionary → fallback to PT name")
        df_product.loc[not_found_mask, 'category_name_en'] = df_product.loc[not_found_mask, 'category_name_pt']

    # Deduplicazione
    df_product = df_product.drop_duplicates(subset=['product_id'], keep='first')
    after_dedup = len(df_product)

    log.info(f"---------- quality report dim_product ----------")
    log.info(f"[dim_product] Input rows        : {total_input}")
    log.info(f"[dim_product] Null categories   : {null_count}")
    log.info(f"[dim_product] Unique product_id : {df_product['product_id'].nunique()}")
    log.info(f"[dim_product] Deduplicated      : {before_dedup} → {after_dedup} rows "
             f"({before_dedup - after_dedup} duplicates removed)")
    log.info(f"[dim_product] Top 5 categories  : {df_product['category_name_en'].value_counts().head(5).to_dict()}")

    df_product = df_product.rename(columns={'product_id': 'natural_key'})
    return df_product[['natural_key', 'category_name_pt', 'category_name_en']]

def transform_review_info(df: pd.DataFrame) -> pd.DataFrame:
    data_frame_review_copy = df.copy()
    total_input = len(data_frame_review_copy)


    invalid_mask = ~data_frame_review_copy['review_score'].between(1, 5)
    invalid_mask_count = invalid_mask.sum()
    if invalid_mask_count > 0:
        log.warning(f"[review_info] {invalid_mask_count} review_score not in range between [1, 5] -> NaN")
        data_frame_review_copy.loc[invalid_mask, 'review_score'] = np.nan

    """
    Devo calcolare la media e togliere i duplicati degli ordini
    """
    order_review_avg = 0
    before_dedup = len(data_frame_review_copy)
    lookup = (
        data_frame_review_copy.groupby('order_id')['review_score']
        .mean()
        .round(1)
        .reset_index()
    )
    after_dedup = len(lookup)

    order_review_avg = lookup['review_score'].mean()
    log.info(f"---------- quality report reviews ----------")
    log.info(f"[reviews] Input rows      : {total_input}")
    log.info(f"[reviews] Unique review_id : {data_frame_review_copy['review_id'].nunique()}")
    log.info(
        f"[reviews] Deduplicated: {before_dedup} → {after_dedup} rows " f"({before_dedup - after_dedup} duplicates removed)")
    log.info(f"[reviews] Avg review score : {order_review_avg:.2f}")

    return lookup


"""
olist_order_items_dataset.csv     → order_id, order_item_id, product_id, seller_id, price, freight_value
olist_order_payments_dataset.csv  → order_id → payment_value (somma per ordine) check
olist_orders_dataset.csv          → order_id → customer_id, delivery_days check 
olist_order_reviews_dataset.csv   → order_id → review_score check
Il campo di matching tra tutte le sorgenti è order_id.
"""

"""
Passo 1 — Base: olist_order_items_dataset.csv
Questa è la sorgente principale perché definisce la granularità della fact: ogni riga è un order_item (un prodotto in un ordine). La natural_key sarà composita:
natural_key = order_id + "_" + str(order_item_id)
"abc123_1", "abc123_2"  ← due prodotti dello stesso ordine
"""

"""
Passo 2 — Matching payment_value da payments
Un ordine può avere più pagamenti — vuoi la somma totale per ordine:
payment_agg = df_payments.groupby('order_id')['payment_value'].sum().reset_index()
abc123 → 170.00  (150 carta + 20 voucher)
"""

"""
Passo 3 — Matching customer_id e delivery_days da orders
Hai già questo DataFrame come secondo elemento del return di transform_dim_date:
df_orders_lookup = df[['natural_key', 'customer_id']] dal return di transform_dim_date
"""
def transform_fact_table(
    df_items: pd.DataFrame,
    df_customer_lookup: pd.DataFrame,
    df_delivery_lookup: pd.DataFrame,
    df_payment_type_lookup: pd.DataFrame,
    df_payment_value_lookup: pd.DataFrame,
    df_review_lookup: pd.DataFrame
) -> pd.DataFrame:
    items_data_frame_copy = df_items.copy()
    total_input = len(items_data_frame_copy)

    # creazione della natural key composta
    items_data_frame_copy['natural_key'] = items_data_frame_copy['order_id'] + '_' + items_data_frame_copy['order_item_id'].astype(str)

    items_data_frame_copy['price'] = pd.to_numeric(items_data_frame_copy['price'], errors='coerce')
    items_data_frame_copy['freight_value'] = pd.to_numeric(items_data_frame_copy['freight_value'], errors='coerce')


    # join su tutti i lookup
    items_data_frame_copy = (
        items_data_frame_copy
        .merge(
            df_customer_lookup.rename(columns={'natural_key': 'order_id'}),
            on='order_id', how='left')
    )


    items_data_frame_copy = (
        items_data_frame_copy
        .merge(
            df_delivery_lookup.rename(columns={'natural_key': 'order_id'}),
                                                        on='order_id', how='left')
    )

    items_data_frame_copy = (
        items_data_frame_copy
        .merge(
            df_payment_type_lookup.rename(columns={'natural_key': 'order_id'}),
                                                        on='order_id', how='left')
    )

    items_data_frame_copy = (
        items_data_frame_copy
        .merge(df_payment_value_lookup.rename(columns={'natural_key': 'order_id'}),
                                                        on='order_id', how='left')
    )

    items_data_frame_copy = (
        items_data_frame_copy
        .merge(df_review_lookup.rename(columns={'natural_key': 'order_id'}),
               on='order_id', how='left')
    )

    # cleaning delle misure
    for column in ['price', 'freight_value', 'payment_value']:
        null_count = items_data_frame_copy[column].isnull().sum()
        if null_count > 0:
            log.warning(f"[fact_vendita] {null_count} null {column} → 0")
            items_data_frame_copy[column] = items_data_frame_copy[column].fillna(0)

        negative_mask = items_data_frame_copy[column] < 0
        if negative_mask.any():
            log.warning(f"[fact_vendita] {negative_mask.sum()} negative {column} → 0")
            items_data_frame_copy.loc[negative_mask, column] = 0

    invalid_review = ~items_data_frame_copy['review_score'].between(1, 5) & items_data_frame_copy['review_score'].notna()
    if invalid_review.any():
        log.warning(f"[fact_vendita] {invalid_review.sum()} invalid review_score → NaN")
        items_data_frame_copy.loc[invalid_review, 'review_score'] = np.nan

    # delivery_days: negativi → NaN (già gestito nel lookup, doppio check)
    invalid_delivery = items_data_frame_copy['delivery_days'] < 0
    if invalid_delivery.any():
        log.warning(f"[fact_vendita] {invalid_delivery.sum()} negative delivery_days → NaN")
        items_data_frame_copy.loc[invalid_delivery, 'delivery_days'] = np.nan

    log.info(f"---------- quality report fact_vendita ----------")
    log.info(f"[fact_vendita] Input rows         : {total_input}")
    log.info(f"[fact_vendita] Output rows        : {len(items_data_frame_copy)}")
    log.info(f"[fact_vendita] Null customer_id   : {items_data_frame_copy['customer_id'].isna().sum()}")
    log.info(f"[fact_vendita] Null payment_type  : {items_data_frame_copy['payment_type'].isna().sum()}")
    log.info(f"[fact_vendita] Null review_score  : {items_data_frame_copy['review_score'].isna().sum()}")
    log.info(f"[fact_vendita] Null delivery_days : {items_data_frame_copy['delivery_days'].isna().sum()}")
    log.info(f"[fact_vendita] Avg price          : {items_data_frame_copy['price'].mean():.2f}")
    log.info(f"[fact_vendita] Avg freight_value  : {items_data_frame_copy['freight_value'].mean():.2f}")
    log.info(f"[fact_vendita] Avg review_score   : {items_data_frame_copy['review_score'].mean():.2f}")
    log.info(f"[fact_vendita] Avg delivery_days  : {items_data_frame_copy['delivery_days'].mean():.1f}")

    # --- Passo 6: Seleziona colonne finali ---
    return items_data_frame_copy[[
        'natural_key',  # order_id_order_item_id
        'order_id',  # per il join con date_id nel load
        'order_item_id',
        'product_id',  # FK → dim_product
        'seller_id',  # FK → dim_seller
        'customer_id',  # FK → dim_customer
        'payment_type',  # FK → dim_payment
        'price',
        'freight_value',
        'payment_value',
        'review_score',
        'delivery_days'
    ]]