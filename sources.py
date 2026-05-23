SOURCES = {
    "dim_seller": {
        "file": "data/raw/olist_sellers_dataset.csv",
        "columns": ["seller_id", "seller_city", "seller_state"]
    },
    "dim_customer": {
        "file": "data/raw/olist_customers_dataset.csv",
        "columns": ["customer_id", "customer_unique_id", "customer_city", "customer_state"]
    },
    "dim_product": {
        "file": "data/raw/olist_products_dataset.csv",
        "columns": ["product_id", "product_category_name"]
    },
    "dim_payment": {
        "file": "data/raw/olist_order_payments_dataset.csv",
        "columns": ["order_id", "payment_type"]
    },
    "dim_date": {
        "file": "data/raw/olist_orders_dataset.csv",
        "columns": ["order_id","customer_id", "order_purchase_timestamp"]
    },
    "fact_sell": {
        "file": "data/raw/olist_order_items_dataset.csv",
        "columns": ["order_id", "order_item_id", "seller_id", "price", "freight_value"]
    }
}