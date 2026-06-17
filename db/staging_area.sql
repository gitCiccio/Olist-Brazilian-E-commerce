CREATE SCHEMA IF NOT EXISTS staging;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS staging.stg_sellers (
    seller_id TEXT,
    seller_zip_code_prefix TEXT,
    seller_city TEXT,
    seller_state TEXT
);

CREATE TABLE IF NOT EXISTS staging.stg_customers (
    customer_id TEXT,
    customer_unique_id TEXT,
    customer_zip_code_prefix TEXT,
    customer_city TEXT,
    customer_state TEXT
);

CREATE TABLE IF NOT EXISTS staging.stg_products (
    product_id TEXT,
    product_category_name TEXT,
    product_name_length TEXT,
    product_description_lenght TEXT,
    product_photos_qty TEXT,
    product_weight_g TEXT,
    product_length_cm TEXT,
    product_height_cm TEXT,
    product_width_cm TEXT
);

CREATE TABLE IF NOT EXISTS staging.stg_product_category_translation (
    product_category_name TEXT,
    product_category_name_english TEXT
);

CREATE TABLE IF NOT EXISTS staging.stg_order_payments (
    order_id TEXT,
    payment_sequential TEXT,
    payment_type TEXT,
    payment_installments TEXT,
    payment_value TEXT
);

CREATE TABLE IF NOT EXISTS staging.stg_orders (
    order_id TEXT,
    customer_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TEXT,
    order_approved_at TEXT,
    order_delivered_carrier_date TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT
);

CREATE TABLE IF NOT EXISTS staging.stg_geolocation (
    geolocation_zip_code_prefix TEXT,
    geolocation_lat TEXT,
    geolocation_lng TEXT,
    geolocation_city TEXT,
    geolocation_state TEXT
);

CREATE TABLE IF NOT EXISTS staging.stg_order_items (
    order_id TEXT,
    order_item_id TEXT,
    product_id TEXT,
    seller_id TEXT,
    shipping_limit_date TEXT,
    price TEXT,
    freight_value TEXT
);

CREATE TABLE IF NOT EXISTS staging.stg_order_reviews (
    review_id TEXT,
    order_id TEXT,
    review_score TEXT,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TEXT,
    review_answer_timestamp TEXT
);

-- ============================================================
-- ETL CHECKPOINT
-- ============================================================

CREATE TABLE IF NOT EXISTS staging.etl_checkpoint (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_file VARCHAR(255) NOT NULL,
    last_row_extracted INT NOT NULL DEFAULT 0,
    total_rows INT NOT NULL,
    status VARCHAR(50) NOT NULL
        CHECK (status IN ('CREATED', 'RUNNING', 'FAILED', 'COMPLETED')),
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    updated_at TIMESTAMP,
    failed_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_committed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_etl_checkpoint_source
    ON staging.etl_checkpoint (source_file, status, started_at DESC);