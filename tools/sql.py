from pyodbc import Row
from db.connection import get_cursor

def _execute_select():
    pass

def get_single_record(
    *, # TODO: validate all arguments
    table: str,
    criteria: dict[str, object],
    return_columns: str | list[str] = "*",
    order_by: str = "StockCode",
) -> Row:
    
    pass

def get_multiple_records(
        
) -> list[Row]:
    pass

