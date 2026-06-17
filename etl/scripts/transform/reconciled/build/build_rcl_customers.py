from unidecode import unidecode
import pandas as pd

from exception.exceptions import DataCleaningError
from logger.logger import AppLogger

log = AppLogger(name="rcl.customers.build", log_file="rcl_customers.log")

BRAZIL_STATE_TO_REGION = {
    'AC': 'norte',
    'AM': 'norte',
    'AP': 'norte',
    'PA': 'norte',
    'RO': 'norte',
    'RR': 'norte',
    'TO': 'norte',
    'AL': 'nordeste',
    'BA': 'nordeste',
    'CE': 'nordeste',
    'MA': 'nordeste',
    'PB': 'nordeste',
    'PE': 'nordeste',
    'PI': 'nordeste',
    'RN': 'nordeste',
    'SE': 'nordeste',
    'DF': 'centro_oeste',
    'GO': 'centro_oeste',
    'MS': 'centro_oeste',
    'MT': 'centro_oeste',
    'ES': 'sudeste',
    'MG': 'sudeste',
    'RJ': 'sudeste',
    'SP': 'sudeste',
    'PR': 'sul',
    'RS': 'sul',
    'SC': 'sul',
}

STATE_REGEX = r'^[A-Z]{2}$'


def build_rcl_customers(dataframe: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_rcl_customers] Build started")

    if dataframe is None:
        log.error("[build_rcl_customers] Input dataframe is None")
        raise DataCleaningError("Customers dataframe is None")

    if dataframe.empty:
        log.error("[build_rcl_customers] Input dataframe is empty")
        raise DataCleaningError("Customers dataframe is empty")

    df = dataframe.copy()

    df = df.rename(columns={
        # aggiungi qui eventuali alias futuri, se serviranno
        # "customer_zipcode_prefix": "customer_zip_code_prefix",
    })

    required_cols = [
        'customer_id',
        'customer_unique_id',
        'customer_zip_code_prefix',
        'customer_city',
        'customer_state'
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        log.error(f"[build_rcl_customers] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing required columns: {missing}")

    input_rows = len(df)
    log.info(f"[build_rcl_customers] Input rows: {input_rows}")

    null_city_count = df['customer_city'].isna().sum()
    null_state_count = df['customer_state'].isna().sum()
    null_unique_id_count = df['customer_unique_id'].isna().sum()

    log.info(f"[build_rcl_customers] Null customer_city: {null_city_count}")
    log.info(f"[build_rcl_customers] Null customer_state: {null_state_count}")
    log.info(f"[build_rcl_customers] Null customer_unique_id: {null_unique_id_count}")

    df['customer_city'] = (
        df['customer_city']
        .fillna('unknown')
        .astype(str)
        .str.strip()
        .str.lower()
        .apply(unidecode)
    )

    df['customer_state'] = (
        df['customer_state']
        .fillna('XX')
        .astype(str)
        .str.strip()
        .str.upper()
    )

    invalid_mask = ~df['customer_state'].str.match(STATE_REGEX, na=False)
    invalid_state_count = invalid_mask.sum()

    if invalid_state_count > 0:
        log.warning(
            f"[build_rcl_customers] Invalid customer_state found: "
            f"{invalid_state_count} -> 'XX'"
        )
        df.loc[invalid_mask, 'customer_state'] = 'XX'
    else:
        log.info("[build_rcl_customers] No invalid customer_state found")

    df['customer_region'] = (
        df['customer_state']
        .map(BRAZIL_STATE_TO_REGION)
        .fillna('unknown')
    )

    df['state_valid_flag'] = df['customer_state'] != 'XX'

    xx_state_count = (df['customer_state'] == 'XX').sum()
    unknown_region_count = (df['customer_region'] == 'unknown').sum()

    log.info(f"[build_rcl_customers] customer_state='XX' rows: {xx_state_count}")
    log.info(f"[build_rcl_customers] customer_region='unknown' rows: {unknown_region_count}")

    before_dedup_rows = len(df)
    df = df.drop_duplicates()
    duplicates_removed = before_dedup_rows - len(df)

    log.info(f"[build_rcl_customers] Exact duplicates removed: {duplicates_removed}")
    log.info(f"[build_rcl_customers] Output rows for rcl_customers: {len(df)}")
    log.info("[build_rcl_customers] Build completed")

    return df[[
        'customer_id',
        'customer_unique_id',
        'customer_zip_code_prefix',
        'customer_city',
        'customer_state',
        'customer_region',
        'state_valid_flag'
    ]]