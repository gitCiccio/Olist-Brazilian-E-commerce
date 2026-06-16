from etl.scripts.data_quality.dq_utils import build_dq_report, save_dq_report


def run_dq_dim_product(source_df, transformed_df, engine_dw):
    report = build_dq_report(
        job_name="dq_dim_product",
        source_df=source_df,
        transformed_df=transformed_df,
        engine_dw=engine_dw,
        loaded_table_name="dim_product",
        required_columns_source=["product_id"],
        required_columns_transformed=["natural_key"],
        business_key_columns_source=["product_id"],
        business_key_columns_transformed=["natural_key"]
    )
    return save_dq_report(report)