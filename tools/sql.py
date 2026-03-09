from pyodbc import Row
from typing import Optional
from collections.abc import Sequence

from db.connection import get_cursor, get_dev_cursor
from tools.validation import check_if_wildcard
from tools.transform import substitute_wildcard

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

    with get_dev_cursor() as cursor:
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
                sql.append(f"WHERE {col} LIKE ?")
            else:
                sql.append(f"AND {col} LIKE ?")
        else:
            if len(params) == 0:
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
        return cursor.fetchall()


def append_single_record(
    *,
    table: str,
    post_data: dict[str, object],
) -> None:
    
    if not post_data:
        return

    # validate_table(table)

    # Use a fixed column order so values line up
    columns = list(post_data.keys())
    placeholders = ", ".join("?" for _ in columns)
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

    values = [post_data[column] for column in columns]

    with get_dev_cursor() as cursor:
        cursor.execute(sql, values)
        cursor.connection.commit()


def append_multiple_records(
    *,
    table: str,
    rows: Sequence[dict[str, object]],
) -> None:
    if not rows:
        return

    # validate_table(table)

    # Use the first row to define the schema for this batch
    columns = list(rows[0].keys())
    placeholders = ", ".join("?" for _ in columns)
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

    # Optional: sanity check that all rows have the same keys
    for i, row in enumerate(rows):
        if row.keys() != rows[0].keys():
            raise ValueError(f"Row {i} has different columns to row 0")

    param_sets = [
        [row[column] for column in columns]
        for row in rows
    ]

    with get_cursor() as cursor:
        cursor.executemany(sql, param_sets)
        cursor.connection.commit()


def update_records(
    *,
    table: str,
    criteria: dict[str, object],
    update_data: dict[str, object]
) -> None:
    
    if not update_data:
        return
    
    # validate_table(table)
    
    # 1. Build the dynamic parts using placeholders instead of values
    set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
    where_clause = " AND ".join([f"{k} = ?" for k in criteria.keys()])

    # 2. Combine into a template (table names cannot be parameterized, so validate them)
    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

    # 3. Combine all values into a single sequence in the same order
    # Values for SET come first, followed by values for WHERE
    params = list(update_data.values()) + list(criteria.values())

    # 4. Execute safely
    with get_dev_cursor() as cursor:
        cursor.execute(sql, tuple(params))
        cursor.connection.commit()