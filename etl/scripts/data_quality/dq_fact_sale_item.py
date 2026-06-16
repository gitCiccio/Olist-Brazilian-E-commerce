from etl.scripts.data_quality.dq_utils import build_dq_report, save_dq_report


def run_dq_fact_sale_item(source_df, transformed_df, engine_dw):
    report = build_dq_report(
        job_name="dq_fact_sale_item",
        source_df=source_df,
        transformed_df=transformed_df,
        engine_dw=engine_dw,
        loaded_table_name="fact_sale_item",
        required_columns_source=[
            "order_id", "order_item_id", "product_natural_key",
            "customer_natural_key", "seller_natural_key", "purchase_date"
        ],
        required_columns_transformed=[
            "natural_key", "order_id", "order_item_id", "product_natural_key",
            "customer_natural_key", "seller_natural_key", "purchase_date"
        ],
        business_key_columns_source=["order_id", "order_item_id"],
        business_key_columns_transformed=["natural_key"],
        numeric_ranges_transformed={
            "price": {"min": 0, "max": None},
            "freight_value": {"min": 0, "max": None},
            "item_count": {"min": 1, "max": None}
        }
    )
    return save_dq_report(report)