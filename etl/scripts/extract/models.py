from dataclasses import dataclass
"""
Classe helper che restituisce un dizionario anonimo 
rende la gestione del codice più chiara e intuitiva
"""
# @dataclass annotazione che evita di creare i costruttori a mano
@dataclass
class CsvMetadata:
    source_file: str
    available_columns: list[str]
    selected_columns: list[str]
    total_rows: int

@dataclass
class CheckpointInfo:
    id: str
    source_file: str
    total_rows: int
    last_row_extracted: int
    status: str
