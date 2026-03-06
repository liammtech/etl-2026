from pyodbc import Row
from db.connection import get_cursor
from typing import Optional

def _execute_select():
    pass

# All below functions assume a single table
# Getters with joins may be added at a later date when need becomes apparent

# TODO: validate all sql function arguments

def get_single_record(
    *, 
    table: str,
    criteria: dict[str, object],
    return_columns: str | list[str] = "*",
    order_by: str = "StockCode"
) -> Row: 
    pass

def get_multiple_records(
    *, 
    table: str,
    criteria: dict[str, object],
    return_columns: str | list[str] = "*",
    order_by: str = "StockCode"
) -> list[Row]:
    pass

def set_single_record(
    *,
    table: str,
    post_data: dict[str, object]
):
    pass

def set_multiple_records(
    *,
    table: str,
    post_data: dict[str, object]
):
    
    pass

