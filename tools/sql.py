from pyodbc import Row
from collections.abc import Sequence

from db.connection import get_cursor
from validation.general_validation import check_if_wildcard
from tools.transform import substitute_wildcard

# All below functions assume a single table
# Getters with joins may be added at a later date when need becomes apparent

# TODO: validate all sql function arguments:
# Certainly make a list of "allowed tables", and implement this as a filter
# Whether or not it is worth it to validate all column names within a table before any SQL ops, is TBD
# May save on transactions, but it means instituting a way to automatically refresh the table schemas
# Can't reliably maintain by hand; table schema changes may come unannounced
# SQL op errors tend to make the failed parameter quite clear anyway (maybe formalise an error depending on SQL response)

def get_single_record(
    *, 
    table: str,
    criteria: dict[str, object],
    return_columns: str | list[str] = "*",
    flatten: bool = False
) -> Row: 
    # Validation to go here

    if type(return_columns) != str:
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
    # print(final_sql)
    # print(criteria)

    with get_cursor() as cursor:
        cursor.execute(final_sql, params)
        fetch_result = cursor.fetchone()

        if flatten:
            if len(fetch_result) > 1:
                print("Cannot flatten SQL fetch result, more than one data item returned")
            else:
                return fetch_result[0]
        else:
            return fetch_result

def get_multiple_records(
    *, 
    table: str,
    criteria: dict[str, object],
    return_columns: list[str] = "*",
    order_by: str = "StockCode"
) -> list[Row]:
    
    print(f"Table is {table}")
    print(f"Criteria is {criteria}")
    print(f"Criteria type is {type(criteria)}")
    return_columns = ", ".join(return_columns)

    sql = [f"SELECT {return_columns} FROM {table}"]
    params = []

    for col, val in criteria.items():
  
        if val == None:
            continue

        if type(val) == list:
            first_iter = True
            for subval in val:
                wildcard_flag = check_if_wildcard(subval)

                sql_operator = "AND (" if first_iter else "OR"

                if wildcard_flag:
                    subval = substitute_wildcard(subval)

                    if len(params) == 0:
                        sql.append(f"WHERE ( {col} LIKE ?")
                    else:
                        sql.append(f"{sql_operator} {col} LIKE ?")

                else:
                    if len(params) == 0:
                        sql.append(f"WHERE ( {col} = ?")
                    else:
                        sql.append(f"{sql_operator} {col} = ?")

                # print(type(subval))
                params.append(subval[0] if isinstance(subval, Row) else subval)
                first_iter = False
            sql.append(")")
            continue

        # print(f"Val is {val}")
        wildcard_flag = check_if_wildcard(val)

        if wildcard_flag:
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

    with get_cursor() as cursor:
        # print(final_sql)
        # print(params)
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

    with get_cursor() as cursor:
        cursor.execute(sql, values)
        cursor.connection.commit()


def append_multiple_records(
    *,
    table: str,
    rows: Sequence[dict[str, object]]
) -> None:
    if not rows:
        print("tools.sql.append_multiple_records(): No rows provided, terminating.")
        return

    # validate_table(table)

    # Use the first row to define the schema for this batch
    columns = list(rows[0].keys())
    column_names = ", ".join(f"[{col}]" for col in columns)
    placeholders = ", ".join("?" for _ in columns)

    sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"


    # Optional: sanity check that all rows have the same keys
    for i, row in enumerate(rows):
        if row.keys() != rows[0].keys():
            raise ValueError(f"Row {i} has different columns to row 0")

    param_sets = [
        [row[column] for column in columns]
        for row in rows
    ]

    # print(f"SQL is: \n{sql}")
    # print(f"param_sets are: \n{param_sets}")

    with get_cursor() as cursor:
        cursor.executemany(sql, param_sets)
        cursor.connection.commit()


def update_records(
    *,
    table: str,
    criteria: dict[str, object],
    update_data: dict[str, object],
    
) -> None:
    
    if not update_data:
        return
    
    # validate_table(table)
    
    def get_op(v):
        return "LIKE" if isinstance(v, str) and ("%" in v or "_" in v) else "="

    set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
    where_clause = " AND ".join([f"{k} {get_op(v)} ?" for k, v in criteria.items()])

    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    params = list(update_data.values()) + list(criteria.values())

    with get_cursor() as cursor:
        cursor.execute(sql, tuple(params))
        cursor.connection.commit()

def delete_records(
    *,
    table: str,
    criteria: dict[str, object],
) -> None:

    if not criteria:
        print("tools.sql.delete_records(): No criteria provided, terminating.")
        return
    
    def get_op(v):
        return "LIKE" if isinstance(v, str) and ("%" in v or "_" in v) else "="
    
    where_clause = " AND ".join([f"{k} {get_op(v)} ?" for k, v in criteria.items()])

    sql = f"DELETE FROM {table} WHERE {where_clause}"
    params = list(criteria.values())

    with get_cursor() as cursor:
        cursor.execute(sql, tuple(params))
        cursor.connection.commit()