CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE staging.stg_sellers (
    seller_id           TEXT,
    seller_zip_code     TEXT,
    seller_city         TEXT,
    seller_state        TEXT
);

CREATE TABLE staging.stg_customers (
    customer_id         TEXT,
    customer_unique_id  TEXT,
    customer_zip_code   TEXT,
    customer_city       TEXT,
    customer_state      TEXT
);

CREATE TABLE staging.stg_products (
    product_id                  TEXT,
    product_category_name       TEXT,
    product_name_length         TEXT,
    product_description_length  TEXT,
    product_photos_qty          TEXT,
    product_weight_g            TEXT,
    product_length_cm           TEXT,
    product_height_cm           TEXT,
    product_width_cm            TEXT
);

CREATE TABLE staging.stg_order_payments (
    order_id                TEXT,
    payment_type            TEXT,
    payment_installments    TEXT,
    payment_value           TEXT
);

CREATE TABLE staging.stg_orders (
    order_id                        TEXT,
    customer_id                     TEXT,
    order_status                    TEXT,
    order_purchase_timestamp        TEXT,
    order_approved_at               TEXT,
    order_delivered_carrier_date    TEXT,
    order_delivered_customer_date   TEXT,
    order_estimated_delivery_date   TEXT
);

CREATE TABLE staging.stg_order_items (
    order_id            TEXT,
    order_item_id       TEXT,
    product_id          TEXT,
    seller_id           TEXT,
    shipping_limit_date TEXT,
    price               TEXT,
    freight_value       TEXT
);

CREATE TABLE staging.stg_order_reviews (
    review_id               TEXT,
    order_id                TEXT,
    review_score            TEXT
);