CREATE SCHEMA IF NOT EXISTS reconciled;

CREATE TABLE IF NOT EXISTS reconciled.rcl_customers (
    customer_id                  TEXT NOT NULL,
    customer_unique_id           TEXT NOT NULL,
    customer_zip_code_prefix     TEXT,
    customer_city                TEXT NOT NULL,
    customer_state               TEXT NOT NULL,
    customer_region              TEXT NOT NULL,
    state_valid_flag             BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS reconciled.rcl_sellers (
    seller_id                    TEXT NOT NULL,
    seller_zip_code_prefix       TEXT,
    seller_city                  TEXT NOT NULL,
    seller_state                 TEXT NOT NULL,
    seller_region                TEXT NOT NULL,
    state_valid_flag             BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS reconciled.rcl_orders (
    order_id                     TEXT NOT NULL,
    customer_id                  TEXT NOT NULL,
    order_status                 TEXT NOT NULL,
    order_purchase_timestamp     TIMESTAMP,
    order_approved_at            TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reconciled.rcl_order_items (
    order_id                     TEXT NOT NULL,
    order_item_id                INTEGER,
    product_id                   TEXT NOT NULL,
    seller_id                    TEXT NOT NULL,
    shipping_limit_date          TIMESTAMP,
    price                        NUMERIC(10,2),
    freight_value                NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS reconciled.rcl_order_payments (
    order_id                     TEXT NOT NULL,
    payment_sequential           INTEGER,
    payment_type                 TEXT NOT NULL,
    payment_installments         INTEGER,
    payment_value                NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS reconciled.rcl_order_reviews (
    review_id                    TEXT NOT NULL,
    order_id                     TEXT NOT NULL,
    review_score                 INTEGER,
    review_comment_title         TEXT,
    review_comment_message       TEXT,
    review_creation_date         TIMESTAMP,
    review_answer_timestamp      TIMESTAMP,
    review_score_valid_flag      BOOLEAN
);

CREATE TABLE IF NOT EXISTS reconciled.rcl_products (
    product_id                   TEXT NOT NULL,
    product_category_name        TEXT NOT NULL,
    product_name_length          INTEGER,
    product_description_length   INTEGER,
    product_photos_qty           INTEGER,
    product_weight_g             NUMERIC(10,2),
    product_length_cm            NUMERIC(10,2),
    product_height_cm            NUMERIC(10,2),
    product_width_cm             NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS reconciled.rcl_product_category_translation (
    product_category_name        TEXT NOT NULL,
    product_category_name_english TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reconciled.rcl_geolocation (
    geolocation_zip_code_prefix  TEXT,
    geolocation_lat              NUMERIC(12,8),
    geolocation_lng              NUMERIC(12,8),
    geolocation_city             TEXT NOT NULL,
    geolocation_state            TEXT NOT NULL
);