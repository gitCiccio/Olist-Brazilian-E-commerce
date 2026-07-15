from etl.scripts.data_quality.dq_utils import build_dq_report, save_dq_report


def run_dq_dim_payment(source_df, transformed_df, engine_dw):
    """
    Esegue i controlli di Data Quality per la dimensione 'dim_payment'.
    - Verifica che il tipo di pagamento e le rate siano popolati.
    - Controlla l'unicità della chiave di business (combinazione tipo-rate).
    - Valida i tipi di pagamento contro una whitelist prefissata.
    - Controlla che il numero di rate sia compreso in un range logico (0-100).

    :param source_df: DataFrame dei dati di pagamento grezzi.
    :param transformed_df: DataFrame dei dati trasformati prima del caricamento.
    :param engine_dw: Connessione al Data Warehouse per verificare le righe caricate.
    :return: Il percorso al file di report JSON generato.
    """
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