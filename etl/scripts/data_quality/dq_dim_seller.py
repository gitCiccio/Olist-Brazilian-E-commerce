from etl.scripts.data_quality.dq_utils import build_dq_report, save_dq_report


def run_dq_dim_seller(source_df, transformed_df, engine_dw):
    report = build_dq_report(
        job_name="dq_dim_seller",
        source_df=source_df,
        transformed_df=transformed_df,
        engine_dw=engine_dw,
        loaded_table_name="dim_seller",
        required_columns_source=["seller_id", "seller_region", "seller_city", "seller_state"],
        required_columns_transformed=["natural_key", "seller_region", "seller_city", "seller_state"],
        business_key_columns_source=["seller_id"],
        business_key_columns_transformed=["natural_key"],
        allowed_values_transformed={
            "seller_state": [
                "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
                "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO","XX"
            ]
        }
    )
    return save_dq_report(report)