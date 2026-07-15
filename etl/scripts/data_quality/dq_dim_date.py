from etl.scripts.data_quality.dq_utils import build_dq_report, save_dq_report


def run_dq_dim_date(source_df, transformed_df, engine_dw):
    """
    Esegue i controlli di Data Quality per la dimensione 'dim_date'.
    - Verifica che la colonna `full_date` (utilizzata sia come required che come business key) 
      sia sempre popolata e non presenti duplicati.

    :param source_df: DataFrame dei dati contenente le date raw.
    :param transformed_df: DataFrame dei dati temporali espansi.
    :param engine_dw: Connessione al Data Warehouse per verificare le righe caricate.
    :return: Il percorso al file di report JSON generato.
    """
    report = build_dq_report(
        job_name="dq_dim_date",
        source_df=source_df,
        transformed_df=transformed_df,
        engine_dw=engine_dw,
        loaded_table_name="dim_date",
        required_columns_source=["full_date"],
        required_columns_transformed=["full_date"],
        business_key_columns_source=["full_date"],
        business_key_columns_transformed=["full_date"]
    )
    return save_dq_report(report)