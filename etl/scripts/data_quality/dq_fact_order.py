from etl.scripts.data_quality.dq_utils import build_dq_report, save_dq_report


def run_dq_fact_order(source_df, transformed_df, engine_dw):
    extra_metrics = {}
    if "delivery_days" in transformed_df.columns:
        extra_metrics["negative_delivery_days"] = int(
            transformed_df["delivery_days"].dropna().lt(0).sum()
        )

    report = build_dq_report(
        job_name="dq_fact_order",
        source_df=source_df,
        transformed_df=transformed_df,
        engine_dw=engine_dw,
        loaded_table_name="fact_order",
        required_columns_source=[
            "order_id", "customer_natural_key", "purchase_date"
        ],
        required_columns_transformed=[
            "natural_key", "order_id", "customer_natural_key", "purchase_date"
        ],
        business_key_columns_source=["order_id"],
        business_key_columns_transformed=["natural_key"],
        allowed_values_transformed={
            "payment_type": ["credit_card", "debit_card", "voucher", "ticket", "not_defined"]
        },
        numeric_ranges_transformed={
            "payment_value": {"min": 0, "max": None},
            "review_score": {"min": 0, "max": 5}
        },
        extra_metrics=extra_metrics
    )
    return save_dq_report(report)