\c olist_dw;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- DIMENSIONI
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_product (
    surrogate_key       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key         VARCHAR(255) NOT NULL UNIQUE,
    category_name_en    VARCHAR(255) NOT NULL,
    product_weight_g    INTEGER,
    product_length_cm   INTEGER,
    product_height_cm   INTEGER,
    product_width_cm    INTEGER
);

CREATE TABLE IF NOT EXISTS dim_date (
    surrogate_key       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key         INTEGER NOT NULL UNIQUE,
    full_date           DATE NOT NULL UNIQUE,
    day                 SMALLINT NOT NULL,
    month               SMALLINT NOT NULL,
    quarter             SMALLINT NOT NULL,
    year                SMALLINT NOT NULL,
    day_of_week         SMALLINT NOT NULL,
    week_of_year        SMALLINT NOT NULL,
    is_weekend          BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_payment (
    surrogate_key           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_type            VARCHAR(100) NOT NULL,
    payment_installments    SMALLINT NOT NULL,
    CONSTRAINT uq_dim_payment UNIQUE (payment_type, payment_installments)
);

CREATE TABLE IF NOT EXISTS dim_customer (
    surrogate_key       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key         VARCHAR(255) NOT NULL,           -- customer_unique_id
    customer_region     VARCHAR(50) NOT NULL,
    customer_city       VARCHAR(255) NOT NULL,
    customer_state      CHAR(2) NOT NULL,
    valid_from          DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to            DATE,
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_dim_customer_dates
        CHECK (valid_to IS NULL OR valid_to >= valid_from)
);

CREATE TABLE IF NOT EXISTS dim_seller (
    surrogate_key       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key         VARCHAR(255) NOT NULL,           -- seller_id
    seller_region       VARCHAR(50) NOT NULL,
    seller_city         VARCHAR(255) NOT NULL,
    seller_state        CHAR(2) NOT NULL,
    valid_from          DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to            DATE,
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_dim_seller_dates
        CHECK (valid_to IS NULL OR valid_to >= valid_from)
);

-- ============================================================
-- FACT TABLE UNICA: livello order_item
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_sale_item (
    surrogate_key               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key                 VARCHAR(255) NOT NULL UNIQUE, -- order_id || '-' || order_item_id
    order_id                    VARCHAR(255) NOT NULL,
    order_item_id               SMALLINT NOT NULL,
    order_status                VARCHAR(50) NOT NULL,
    item_count                  SMALLINT NOT NULL DEFAULT 1,
    price                       DECIMAL(10,2) NOT NULL,
    freight_value               DECIMAL(10,2) NOT NULL,
    review_score                DECIMAL(3,1),

    product_key                 UUID NOT NULL,
    customer_key                UUID NOT NULL,
    seller_key                  UUID NOT NULL,
    payment_key                 UUID,
    purchase_date_key           UUID NOT NULL,
    shipping_limit_date_key     UUID,
    delivered_date_key          UUID,
    estimated_delivery_date_key UUID,

    CONSTRAINT fk_fact_item_product
        FOREIGN KEY (product_key) REFERENCES dim_product(surrogate_key),

    CONSTRAINT fk_fact_item_customer
        FOREIGN KEY (customer_key) REFERENCES dim_customer(surrogate_key),

    CONSTRAINT fk_fact_item_seller
        FOREIGN KEY (seller_key) REFERENCES dim_seller(surrogate_key),

    CONSTRAINT fk_fact_item_payment
        FOREIGN KEY (payment_key) REFERENCES dim_payment(surrogate_key),

    CONSTRAINT fk_fact_item_purchase_date
        FOREIGN KEY (purchase_date_key) REFERENCES dim_date(surrogate_key),

    CONSTRAINT fk_fact_item_shipping_limit_date
        FOREIGN KEY (shipping_limit_date_key) REFERENCES dim_date(surrogate_key),

    CONSTRAINT fk_fact_item_delivered_date
        FOREIGN KEY (delivered_date_key) REFERENCES dim_date(surrogate_key),

    CONSTRAINT fk_fact_item_estimated_delivery_date
        FOREIGN KEY (estimated_delivery_date_key) REFERENCES dim_date(surrogate_key)
);

-- ============================================================
-- VINCOLI SCD2
-- ============================================================

CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_customer_current
    ON dim_customer (natural_key)
    WHERE is_current = TRUE;

CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_seller_current
    ON dim_seller (natural_key)
    WHERE is_current = TRUE;

-- ============================================================
-- INDICI UTILI PER LA FACT TABLE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_sale_item_order_id
    ON fact_sale_item (order_id);

CREATE INDEX IF NOT EXISTS idx_fact_sale_item_customer
    ON fact_sale_item (customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_sale_item_seller
    ON fact_sale_item (seller_key);

CREATE INDEX IF NOT EXISTS idx_fact_sale_item_payment
    ON fact_sale_item (payment_key);