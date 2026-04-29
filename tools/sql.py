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

        params.append(str(val)) # HERE IS THE PROBLEM

    if table == "BomStructure" or table == "[BomStructure+]":
        order_by = "ParentPart"

    final_sql = " ".join(sql) + f" ORDER BY {order_by}"

    with get_cursor() as cursor:
        print(final_sql)
        print(params)
        cursor.execute(final_sql, params)
        result = cursor.fetchall()
        print(result)
        return result

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


def append_single_record(
    *,
    table: str,
    row: dict[str, object]
) -> None:
    if not row:
        print("tools.sql.append_single_record(): No row provided, terminating.")
        return

    # validate_table(table)

    print(f"append_single_record():")
    print(f"Table appending to: {table}")
    print(f"Row being appended: {row}")

    columns = list(row.keys())
    column_names = ", ".join(f"[{col}]" for col in columns)
    placeholders = ", ".join("?" for _ in columns)

    sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
    params = [row[column] for column in columns]

    with get_cursor() as cursor:
        cursor.execute(sql, params)
        cursor.connection.commit()


def append_multiple_records(
    *,
    table: str,
    rows: Sequence[dict[str, object]]
) -> None:
    if not rows:
        print("tools.sql.append_multiple_records(): No rows provided, terminating.")
        return
    
    if isinstance(rows[0], Row):
        rows = [dict(zip([column[0] for column in r.cursor_description], r)) for r in rows]

    # validate_table(table)
    first_row = rows[0]
    excluded_keys = {
        k for k, v in first_row.items() 
        if isinstance(v, (bytes, bytearray)) and len(v) == 8 # Standard SQL timestamp size
        or k.lower() in ('TimeStamp')
    }


    # Use the first row to define the schema for this batch
    columns = [k for k in first_row.keys() if k not in excluded_keys]
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

    with get_cursor() as cursor:
        cursor.executemany(sql, param_sets)
        cursor.connection.commit()


def update_records(
    *,
    table: str,
    criteria: dict[str, object],
    update_data: dict[str, object],
    
) -> None:
    print(f"ATTEMPTING TO UPDATE TABLE {table}")
    print(f"UPDATE DATA IS: {update_data}")
    if not update_data:
        return
    
    # validate_table(table)
    
    def get_op(v):
        return "LIKE" if isinstance(v, str) and ("%" in v or "_" in v) else "="

    set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
    where_clause = " AND ".join([f"{k} {get_op(v)} ?" for k, v in criteria.items()])

    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    params = list(update_data.values()) + list(criteria.values())
    print(sql)
    print(params)

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

# To implement later:

# def update_records_case(
#     table: str,
#     target_column: str,
#     value_map: dict[object, object],
#     where: list[tuple[str, str, object]] | None = None,
# ) -> tuple[str, list[object]]:
#     if not value_map:
#         raise ValueError("value_map cannot be empty")

#     case_parts = []
#     params: list[object] = []

#     for old_value, new_value in value_map.items():
#         case_parts.append("WHEN ? THEN ?")
#         params.extend([old_value, new_value])

#     sql = (
#         f"UPDATE {table} "
#         f"SET {target_column} = CASE {target_column} "
#         + " ".join(case_parts)
#         + " END"
#     )

#     extra_where = list(where or [])
#     extra_where.append((target_column, "in", list(value_map.keys())))

#     where_sql_parts = []

#     for column, operator, value in extra_where:
#         op = operator.lower()

#         if op == "=":
#             where_sql_parts.append(f"{column} = ?")
#             params.append(value)

#         elif op == "in":
#             value = list(value)
#             if not value:
#                 raise ValueError(f"IN value for {column} cannot be empty")
#             placeholders = ", ".join("?" for _ in value)
#             where_sql_parts.append(f"{column} IN ({placeholders})")
#             params.extend(value)

#         else:
#             raise ValueError(f"Unsupported operator in this helper: {operator}")

#     sql += " WHERE " + " AND ".join(where_sql_parts)
#     print(sql)
#     print(params)


#     with get_cursor() as cursor:
#         cursor.execute(sql, tuple(params))
#         cursor.connection.commit()