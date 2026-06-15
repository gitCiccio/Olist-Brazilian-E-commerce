from unidecode import unidecode
import pandas as pd
from exception.exceptions import DataCleaningError
from logger.logger import AppLogger

log = AppLogger(name="rcl_customers.extract", log_file="rcl_customers.log")

# Nel tuo reconciled.py, aggiungi questo dizionario vicino agli altri mapping
BRAZIL_STATE_TO_REGION = {
    # NORD (Norte)
    'AC': 'norte',  # Acre
    'AM': 'norte',  # Amazonas
    'AP': 'norte',  # Amapá
    'PA': 'norte',  # Pará
    'RO': 'norte',  # Rondônia
    'RR': 'norte',  # Roraima
    'TO': 'norte',  # Tocantins

    # NORDEST (Nordeste)
    'AL': 'nordeste',  # Alagoas
    'BA': 'nordeste',  # Bahia
    'CE': 'nordeste',  # Ceará
    'MA': 'nordeste',  # Maranhão
    'PB': 'nordeste',  # Paraíba
    'PE': 'nordeste',  # Pernambuco
    'PI': 'nordeste',  # Piauí
    'RN': 'nordeste',  # Rio Grande do Norte
    'SE': 'nordeste',  # Sergipe

    # CENTRO-OVEST (Centro-Oeste)
    'DF': 'centro_oeste',  # Distretto Federale (Brasilia)
    'GO': 'centro_oeste',  # Goiás
    'MS': 'centro_oeste',  # Mato Grosso do Sul
    'MT': 'centro_oeste',  # Mato Grosso

    # SUDEST (Sudeste)
    'ES': 'sudeste',  # Espírito Santo
    'MG': 'sudeste',  # Minas Gerais
    'RJ': 'sudeste',  # Rio de Janeiro
    'SP': 'sudeste',  # São Paulo  ← qui troverai il 40%+ dei clienti

    # SUD (Sul)
    'PR': 'sul',  # Paraná
    'RS': 'sul',  # Rio Grande do Sul
    'SC': 'sul',  # Santa Catarina
}
# Regex
STATE_REGEX = (r'^[A-Z]{2}$')

def rcl_customers_cleaning(dataframe: pd.DataFrame) -> pd.DataFrame:
    log.info("Cleaning RCL Customers")

    if dataframe is None:
        log.error("[rcl_customers_cleaning] dataframe is None")
        raise DataCleaningError("Customers dataframe is None")

    df = dataframe.copy()

    required_cols = [
        'customer_id',
        'customer_unique_id',
        'customer_zip_code_prefix',
        'customer_city',
        'customer_state'
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise DataCleaningError(f"Missing required columns: {missing}")

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
    if invalid_mask.any():
        log.warning(f"[rcl_customers_cleaning] invalid customer_state: {invalid_mask.sum()} -> 'XX'")
        df.loc[invalid_mask, 'customer_state'] = 'XX'

    df['customer_region'] = (
        df['customer_state']
        .map(BRAZIL_STATE_TO_REGION)
        .fillna('unknown')
    )

    df['state_valid_flag'] = df['customer_state'] != 'XX'

    df = df.drop_duplicates()

    return df[[
        'customer_id',
        'customer_unique_id',
        'customer_zip_code_prefix',
        'customer_city',
        'customer_state',
        'customer_region',
        'state_valid_flag'
    ]]