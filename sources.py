SOURCES = {
    "dim_seller": {
        "file": "data/raw/olist_sellers_dataset.csv",
        "columns": ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"],
        "staging_table": "staging.stg_sellers"
    },
    "dim_customer": {
        "file": "data/raw/olist_customers_dataset.csv",
        "columns": ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"],
        "staging_table": "staging.stg_customers"
    },
    "dim_product_category": {
        "file": "data/raw/product_category_name_translation.csv",
        "columns": [
            "product_category_name_english"
        ],
        "staging_table": "staging.stg_product_category_translation"
    },
    "dim_product": {
            "file": "data/raw/olist_products_dataset.csv",
            "columns": [
                "product_id", "product_category_name", "product_name_length",
                "product_description_lenght", "product_photos_qty",
                "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"
            ],
            "staging_table": "staging.stg_products"
        },
    "dim_payment": {
        "file": "data/raw/olist_order_payments_dataset.csv",
        "columns": ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"],
        "staging_table": "staging.stg_order_payments"
    },
    "dim_date": {
        "file": "data/raw/olist_orders_dataset.csv",
        "columns": [
            "order_id", "customer_id", "order_status",
            "order_purchase_timestamp", "order_approved_at",
            "order_delivered_carrier_date", "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ],
        "staging_table": "staging.stg_orders"
    },
    "review_info": {
        "file": "data/raw/olist_order_reviews_dataset.csv",
        "columns": [
            "review_id", "order_id", "review_score",
            "review_comment_title", "review_comment_message",
            "review_creation_date", "review_answer_timestamp"
        ],
        "staging_table": "staging.stg_order_reviews"
    },
    "order_items_info": {
        "file": "data/raw/olist_order_items_dataset.csv",
        "columns": [
            "order_id", "order_item_id", "product_id", "seller_id",
            "shipping_limit_date", "price", "freight_value"
        ],
        "staging_table": "staging.stg_order_items"
    }
}