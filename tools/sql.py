from pyodbc import Row
from typing import Optional

from db.connection import get_cursor
from tools.validation import check_if_wildcard
from tools.transform import substitute_wildcard

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
) -> Row: 
    # Validation to go here

    return_columns = ", ".join(return_columns)

    sql = [f"SELECT {return_columns} FROM {table}"]
    params = []

    for col, val in criteria.items():
        if val == None:
            continue

        if len(params) == 0:
            sql.append(f"WHERE {col} = ?")
        else:
            sql.append(f"AND {col} = ?")

        params.append(val)

    final_sql = " ".join(sql)
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
        
    return_columns = ", ".join(return_columns)

    sql = [f"SELECT {return_columns} FROM {table}"]
    params = []

    for col, val in criteria.items():
        if val == None:
            continue

    wildcard_flag = check_if_wildcard(val)
    
    if wildcard_flag:
        print(f"Wildcard detected: value for {col}")
        val = substitute_wildcard(val)

    if len(params) == 0:
        sql.append(f"WHERE {col} = ?")
    else:
        sql.append(f"AND {col} = ?")

    params.append(val)
    
    if table == "BomStructure" or table == "[BomStructure+]":
        order_by = "ParentPart"

    final_sql = " ".join(sql) + f" ORDER BY {order_by}"
    print(final_sql)

    if len(criteria) == 1:
        one_line = True

    with get_cursor() as cursor:
        cursor.execute(final_sql, params)
        return cursor.fetchone() if one_line else cursor.fetchall()


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
