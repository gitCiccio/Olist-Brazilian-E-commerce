from dataclasses import dataclass

@dataclass
class RclCustomer:
    customer_id: str
    customer_unique_id: str
    customer_zip_code_prefix: str | None
    customer_city: str
    customer_state: str
    customer_region: str
    state_valid_flag: bool