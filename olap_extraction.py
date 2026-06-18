from pathlib import Path
import os
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "exports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Postgres123:_")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "olist_dw")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

QUERIES = {
    "kpi_01_fatturato_per_mese": """
        SELECT
            d.year,
            d.month,
            DATE_TRUNC('month', d.full_date)::date AS month_date,
            SUM(fsi.price) AS revenue_items_only,
            SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
            COUNT(*) AS sold_items
        FROM fact_sale_item fsi
        JOIN dim_date d
            ON fsi.purchase_date_key = d.surrogate_key
        GROUP BY
            d.year,
            d.month,
            DATE_TRUNC('month', d.full_date)
        ORDER BY
            d.year,
            d.month
    """,

    "kpi_02_fatturato_per_trimestre": """
        SELECT
            d.year,
            d.quarter,
            SUM(fsi.price) AS revenue_items_only,
            SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
            COUNT(*) AS sold_items
        FROM fact_sale_item fsi
        JOIN dim_date d
            ON fsi.purchase_date_key = d.surrogate_key
        GROUP BY
            d.year,
            d.quarter
        ORDER BY
            d.year,
            d.quarter
    """,

    "kpi_03_fatturato_per_anno": """
        SELECT
            d.year,
            SUM(fsi.price) AS revenue_items_only,
            SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
            COUNT(*) AS sold_items
        FROM fact_sale_item fsi
        JOIN dim_date d
            ON fsi.purchase_date_key = d.surrogate_key
        GROUP BY
            d.year
        ORDER BY
            d.year
    """,

    "kpi_04_fatturato_per_regione_cliente": """
        SELECT
            dc.customer_region,
            SUM(fsi.price) AS revenue_items_only,
            SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
            COUNT(DISTINCT fsi.order_id) AS orders_count,
            COUNT(*) AS sold_items
        FROM fact_sale_item fsi
        JOIN dim_customer dc
            ON fsi.customer_key = dc.surrogate_key
        WHERE dc.is_current = TRUE
        GROUP BY
            dc.customer_region
        ORDER BY
            revenue_items_only DESC
    """,

    "kpi_05_fatturato_per_stato_cliente": """
        SELECT
            dc.customer_region,
            dc.customer_state,
            SUM(fsi.price) AS revenue_items_only,
            COUNT(DISTINCT fsi.order_id) AS orders_count
        FROM fact_sale_item fsi
        JOIN dim_customer dc
            ON fsi.customer_key = dc.surrogate_key
        WHERE dc.is_current = TRUE
        GROUP BY
            dc.customer_region,
            dc.customer_state
        ORDER BY
            dc.customer_region,
            revenue_items_only DESC
    """,

    "kpi_06_fatturato_per_citta_cliente": """
        SELECT
            dc.customer_region,
            dc.customer_state,
            dc.customer_city,
            SUM(fsi.price) AS revenue_items_only,
            COUNT(DISTINCT fsi.order_id) AS orders_count
        FROM fact_sale_item fsi
        JOIN dim_customer dc
            ON fsi.customer_key = dc.surrogate_key
        WHERE dc.is_current = TRUE
        GROUP BY
            dc.customer_region,
            dc.customer_state,
            dc.customer_city
        ORDER BY
            revenue_items_only DESC
    """,

    "kpi_07_fatturato_per_categoria_prodotto": """
        SELECT
            dp.category_name_en,
            SUM(fsi.price) AS revenue_items_only,
            SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
            COUNT(*) AS sold_items,
            COUNT(DISTINCT fsi.order_id) AS orders_count
        FROM fact_sale_item fsi
        JOIN dim_product dp
            ON fsi.product_key = dp.surrogate_key
        GROUP BY
            dp.category_name_en
        ORDER BY
            revenue_items_only DESC
    """,

    "kpi_08_fatturato_mensile_per_categoria_prodotto": """
        SELECT
            d.year,
            d.month,
            dp.category_name_en,
            SUM(fsi.price) AS revenue_items_only,
            COUNT(*) AS sold_items
        FROM fact_sale_item fsi
        JOIN dim_date d
            ON fsi.purchase_date_key = d.surrogate_key
        JOIN dim_product dp
            ON fsi.product_key = dp.surrogate_key
        GROUP BY
            d.year,
            d.month,
            dp.category_name_en
        ORDER BY
            d.year,
            d.month,
            revenue_items_only DESC
    """,

    "kpi_09_top_seller_per_ricavi": """
        SELECT
            ds.natural_key AS seller_id,
            ds.seller_region,
            ds.seller_state,
            ds.seller_city,
            SUM(fsi.price) AS revenue_items_only,
            SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
            COUNT(DISTINCT fsi.order_id) AS orders_count,
            COUNT(*) AS sold_items
        FROM fact_sale_item fsi
        JOIN dim_seller ds
            ON fsi.seller_key = ds.surrogate_key
        WHERE ds.is_current = TRUE
        GROUP BY
            ds.natural_key,
            ds.seller_region,
            ds.seller_state,
            ds.seller_city
        ORDER BY
            revenue_items_only DESC
        LIMIT 20
    """,

    "kpi_10_numero_ordini_per_mese": """
        SELECT
            d.year,
            d.month,
            DATE_TRUNC('month', d.full_date)::date AS month_date,
            COUNT(*) AS orders_count
        FROM fact_order fo
        JOIN dim_date d
            ON fo.purchase_date_key = d.surrogate_key
        GROUP BY
            d.year,
            d.month,
            DATE_TRUNC('month', d.full_date)
        ORDER BY
            d.year,
            d.month
    """,

    "kpi_11_numero_ordini_per_stato_ordine_mese": """
        SELECT
            d.year,
            d.month,
            fo.order_status,
            COUNT(*) AS orders_count
        FROM fact_order fo
        JOIN dim_date d
            ON fo.purchase_date_key = d.surrogate_key
        GROUP BY
            d.year,
            d.month,
            fo.order_status
        ORDER BY
            d.year,
            d.month,
            orders_count DESC
    """,

    "kpi_12_ticket_medio_per_ordine": """
        SELECT
            d.year,
            d.month,
            ROUND(AVG(fo.payment_value), 2) AS avg_ticket,
            ROUND(SUM(fo.payment_value), 2) AS total_order_value,
            COUNT(*) AS orders_count
        FROM fact_order fo
        JOIN dim_date d
            ON fo.purchase_date_key = d.surrogate_key
        GROUP BY
            d.year,
            d.month
        ORDER BY
            d.year,
            d.month
    """,

    "kpi_13_ticket_medio_per_regione_cliente": """
        SELECT
            dc.customer_region,
            ROUND(AVG(fo.payment_value), 2) AS avg_ticket,
            ROUND(SUM(fo.payment_value), 2) AS total_order_value,
            COUNT(*) AS orders_count
        FROM fact_order fo
        JOIN dim_customer dc
            ON fo.customer_key = dc.surrogate_key
        WHERE dc.is_current = TRUE
        GROUP BY
            dc.customer_region
        ORDER BY
            avg_ticket DESC
    """,

    "kpi_14_tempo_medio_consegna": """
        SELECT
            d.year,
            d.month,
            ROUND(AVG(fo.delivery_days), 2) AS avg_delivery_days,
            MIN(fo.delivery_days) AS min_delivery_days,
            MAX(fo.delivery_days) AS max_delivery_days,
            COUNT(*) AS delivered_orders
        FROM fact_order fo
        JOIN dim_date d
            ON fo.purchase_date_key = d.surrogate_key
        WHERE fo.order_status = 'delivered'
          AND fo.delivery_days IS NOT NULL
        GROUP BY
            d.year,
            d.month
        ORDER BY
            d.year,
            d.month
    """,

    "kpi_15_tempo_medio_consegna_per_regione_cliente": """
        SELECT
            dc.customer_region,
            ROUND(AVG(fo.delivery_days), 2) AS avg_delivery_days,
            COUNT(*) AS delivered_orders
        FROM fact_order fo
        JOIN dim_customer dc
            ON fo.customer_key = dc.surrogate_key
        WHERE fo.order_status = 'delivered'
          AND fo.delivery_days IS NOT NULL
          AND dc.is_current = TRUE
        GROUP BY
            dc.customer_region
        ORDER BY
            avg_delivery_days DESC
    """,

    "kpi_16_review_score_medio_per_regione_cliente": """
        SELECT
            dc.customer_region,
            ROUND(AVG(fo.review_score), 2) AS avg_review_score,
            COUNT(*) AS reviewed_orders
        FROM fact_order fo
        JOIN dim_customer dc
            ON fo.customer_key = dc.surrogate_key
        WHERE fo.review_score IS NOT NULL
          AND dc.is_current = TRUE
        GROUP BY
            dc.customer_region
        ORDER BY
            avg_review_score DESC
    """,

    "kpi_17_review_score_medio_per_mese": """
        SELECT
            d.year,
            d.month,
            ROUND(AVG(fo.review_score), 2) AS avg_review_score,
            COUNT(*) AS reviewed_orders
        FROM fact_order fo
        JOIN dim_date d
            ON fo.purchase_date_key = d.surrogate_key
        WHERE fo.review_score IS NOT NULL
        GROUP BY
            d.year,
            d.month
        ORDER BY
            d.year,
            d.month
    """,

    "kpi_18_distribuzione_metodi_pagamento": """
        SELECT
            dp.payment_type,
            COUNT(*) AS orders_count,
            ROUND(SUM(fo.payment_value), 2) AS total_payment_value,
            ROUND(AVG(fo.payment_value), 2) AS avg_payment_value
        FROM fact_order fo
        JOIN dim_payment dp
            ON fo.payment_key = dp.surrogate_key
        GROUP BY
            dp.payment_type
        ORDER BY
            total_payment_value DESC
    """,

    "kpi_19_distribuzione_metodi_pagamento_rate": """
        SELECT
            dp.payment_type,
            dp.payment_installments,
            COUNT(*) AS orders_count,
            ROUND(SUM(fo.payment_value), 2) AS total_payment_value,
            ROUND(AVG(fo.payment_value), 2) AS avg_payment_value
        FROM fact_order fo
        JOIN dim_payment dp
            ON fo.payment_key = dp.surrogate_key
        GROUP BY
            dp.payment_type,
            dp.payment_installments
        ORDER BY
            dp.payment_type,
            dp.payment_installments
    """,

    "kpi_20_analisi_geografica_cliente_venditore": """
        SELECT
            dc.customer_region,
            ds.seller_region,
            COUNT(DISTINCT fsi.order_id) AS orders_count,
            COUNT(*) AS sold_items,
            SUM(fsi.price) AS revenue_items_only
        FROM fact_sale_item fsi
        JOIN dim_customer dc
            ON fsi.customer_key = dc.surrogate_key
        JOIN dim_seller ds
            ON fsi.seller_key = ds.surrogate_key
        WHERE dc.is_current = TRUE
          AND ds.is_current = TRUE
        GROUP BY
            dc.customer_region,
            ds.seller_region
        ORDER BY
            revenue_items_only DESC
    """,

    "kpi_21_stato_cliente_x_stato_seller": """
        SELECT
            dc.customer_state,
            ds.seller_state,
            COUNT(DISTINCT fsi.order_id) AS orders_count,
            SUM(fsi.price) AS revenue_items_only
        FROM fact_sale_item fsi
        JOIN dim_customer dc
            ON fsi.customer_key = dc.surrogate_key
        JOIN dim_seller ds
            ON fsi.seller_key = ds.surrogate_key
        WHERE dc.is_current = TRUE
          AND ds.is_current = TRUE
        GROUP BY
            dc.customer_state,
            ds.seller_state
        ORDER BY
            revenue_items_only DESC
    """,

    "kpi_22_seller_top_per_categoria_prodotto": """
        SELECT
            dp.category_name_en,
            ds.natural_key AS seller_id,
            ds.seller_state,
            SUM(fsi.price) AS revenue_items_only,
            COUNT(*) AS sold_items
        FROM fact_sale_item fsi
        JOIN dim_product dp
            ON fsi.product_key = dp.surrogate_key
        JOIN dim_seller ds
            ON fsi.seller_key = ds.surrogate_key
        WHERE ds.is_current = TRUE
        GROUP BY
            dp.category_name_en,
            ds.natural_key,
            ds.seller_state
        ORDER BY
            dp.category_name_en,
            revenue_items_only DESC
    """
}

def export_queries():
    with engine.connect() as conn:
        for name, sql in QUERIES.items():
            print(f"Esporto {name}...")
            df = pd.read_sql_query(text(sql), conn)
            output_file = OUTPUT_DIR / f"{name}.csv"
            df.to_csv(output_file, index=False, encoding="utf-8")
            print(f"Creato: {output_file}")

if __name__ == "__main__":
    export_queries()
    print(f"\nEsportazione completata. File salvati in: {OUTPUT_DIR}")