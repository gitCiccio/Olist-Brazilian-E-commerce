from etl.scripts.data_quality.dq_utils import build_dq_report, save_dq_report


def run_dq_dim_payment(source_df, transformed_df, engine_dw):
    report = build_dq_report(
        job_name="dq_dim_payment",
        source_df=source_df,
        transformed_df=transformed_df,
        engine_dw=engine_dw,
        loaded_table_name="dim_payment",
        required_columns_source=["payment_type", "payment_installments"],
        required_columns_transformed=["payment_type", "payment_installments"],
        business_key_columns_source=["payment_type", "payment_installments"],
        business_key_columns_transformed=["payment_type", "payment_installments"],
        allowed_values_transformed={
            "payment_type": ["credit_card", "debit_card", "voucher", "ticket", "not_defined"]
        },
        numeric_ranges_source={
            "payment_installments": {"min": 0, "max": 100}
        },
        numeric_ranges_transformed={
            "payment_installments": {"min": 0, "max": 100}
        }
    )
    return save_dq_report(report)