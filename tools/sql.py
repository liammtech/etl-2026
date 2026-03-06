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
    # Validation to go here

    return_columns = ", ".join(return_columns)

    sql = [f"SELECT {return_columns} FROM {table}"]
    params = []

    for col, val in criteria.items():
        if val == None:
            continue

        if len(params == 0):
            sql.append(f"WHERE {col} = ?")
        else:
            sql.append(f"AND {col} = ?")

        params.append(val)

    if table == "BomStructure" or table == "[BomStructure+]":
        order_by = "ParentPart"

    final_sql = " ".join(sql) + f" ORDER BY {order_by}"
    print(final_sql)

    with get_cursor() as cursor:
        cursor.execute(final_sql, params)
        return cursor.fetchone()

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

