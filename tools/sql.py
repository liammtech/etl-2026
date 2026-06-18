from dataclasses import dataclass
from pyodbc import Cursor, Row
from collections.abc import Sequence
from typing import Any, Literal, NamedTuple

from db.connection import get_cursor
from tools.utils.string_checks import check_if_wildcard
from tools.transform import substitute_wildcard, normalise_sql_value


# TODO: Add table-name validation via an ALLOWED_TABLES whitelist.
#       Table names are interpolated into SQL and cannot be parameterised.

# TODO: Consider dynamic column-name validation from database schema metadata.
#       Avoid maintaining table schemas manually; Syspro schema changes may occur
#       outside this project.

# TODO: Ensure all CRUD helpers share the same criteria handling:
#       equality, LIKE wildcards, comparison operators, and NOT LIKE.

# TODO: Keep JOIN support focused on SELECT helpers unless a concrete joined
#       UPDATE/DELETE use case appears.

'''
JOIN SYNTAX

row = get_single_record(
    table="BomStructure AS b",
    joins=[
        sql.Join(                       # When used in another module, Join class is available via sql module
            table="InvMaster AS i",
            on="b.Component = i.StockCode",
            join_type="INNER"
        )
    ],
    criteria={
        "b.ParentPart": "WFDWLG0895H",
        "b.Route": "0"
    },
    return_columns=[
        "b.ParentPart",
        "b.Component",
        "i.Description",
        "i.StockUom"
    ]
)
'''

VALID_OPS = {"=", "!=", "<>", ">", ">=", "<", "<=", "LIKE", "NOT LIKE"}

TEXT_COLUMNS = {"Route"}

class Join(NamedTuple):
    table: str
    on: str
    join_type: Literal["INNER", "LEFT", "RIGHT"] = "INNER"


def _build_where_clause(
    criteria: dict[str, object],
) -> tuple[str, list[object]]:
    """Build a parameterised SQL WHERE clause from a criteria dictionary.

    Criteria values may be supplied directly for equality checks:

        {"StockCode": "ABC123"}

    Or as an ``(operator, value)`` tuple for explicit comparisons:

        {"Operation": (">", 10)}
        {"Route": ("NOT LIKE", "A*")}

    String values containing application wildcards are automatically
    converted to SQL wildcards using ``substitute_wildcard()`` and matched
    using ``LIKE`` when no explicit operator is supplied.

    Supported comparison operators are defined by ``VALID_OPS``.

    Args:
        criteria: Mapping of column names to filter values or
            ``(operator, value)`` tuples.

    Returns:
        A tuple containing:

        - A parameterised SQL WHERE clause string.
        - A list of parameter values corresponding to the placeholders.

    Raises:
        ValueError: If ``criteria`` is empty.
        ValueError: If an unsupported SQL operator is supplied.

    Examples:
        Equality matching:

            _build_where_clause({
                "StockCode": "FKKH2341",
                "Route": "0",
            })

        Wildcard matching:

            _build_where_clause({
                "StockCode": "FKK?####",
            })

        Comparison operators:

            _build_where_clause({
                "Operation": (">", 10),
            })

        Explicit LIKE matching:

            _build_where_clause({
                "StockCode": ("NOT LIKE", "FKKR*"),
            })
    """
    if not criteria:
        raise ValueError("Criteria cannot be empty.")

    clauses: list[str] = []
    params: list[object] = []

    def _prepare_value(column: str, value: object) -> tuple[str, object]:
        if isinstance(value, Row):
            value = value[0]

        value = normalise_sql_value(column, value)

        op = "="

        if isinstance(value, str) and check_if_wildcard(value):
            value = substitute_wildcard(value)
            op = "LIKE"

        elif isinstance(value, str) and ("%" in value or "_" in value):
            op = "LIKE"

        return op, value

    for column, value in criteria.items():
        if isinstance(value, list):
            sub_clauses: list[str] = []

            for subvalue in value:
                sub_op, subvalue = _prepare_value(column, subvalue)
                sub_clauses.append(f"{column} {sub_op} ?")
                params.append(subvalue)

            clauses.append("(" + " OR ".join(sub_clauses) + ")")
            continue

        if (
            isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[0], str)
        ):
            op = value[0].upper()
            param = value[1]

            if op not in VALID_OPS:
                raise ValueError(f"Invalid SQL operator: {op!r}")

            _, param = _prepare_value(column, param)
        else:
            op, param = _prepare_value(column, value)

        clauses.append(f"{column} {op} ?")
        params.append(param)

    return " AND ".join(clauses), params


def get_single_record(
    *,
    table: str,
    criteria: dict[str, object],
    return_columns: str | list[str] = "*",
    joins: list[Join] | None = None,
    flatten: bool = False,
    strict: bool = False,
    cursor: Cursor | None = None,
) -> Row | object | None:
    """Fetch a single record from a table.

    By default, this returns the first matching row. If ``strict=True``,
    the function raises a ValueError when more than one matching row is found.
    """
    if not isinstance(return_columns, str):
        return_columns = ", ".join(return_columns)

    where_clause, params = _build_where_clause(criteria)

    sql = [f"SELECT {return_columns} FROM {table}"]

    if joins:
        for join in joins:
            sql.append(
                f"{join.join_type} JOIN {join.table} ON {join.on}"
            )

    sql.append(f"WHERE {where_clause}")

    final_sql = " ".join(sql)

    def _execute(active_cursor: Cursor) -> Row | object | None:
        active_cursor.execute(final_sql, params)

        if strict:
            rows = active_cursor.fetchmany(2)

            if not rows:
                return None

            if len(rows) > 1:
                raise ValueError(
                    f"Expected one record from {table}, got multiple."
                )

            fetch_result = rows[0]
        else:
            fetch_result = active_cursor.fetchone()

            if fetch_result is None:
                return None

        if flatten:
            if len(fetch_result) > 1:
                raise ValueError(
                    "Cannot flatten SQL fetch result: more than one column returned."
                )

            return fetch_result[0]

        return fetch_result

    if cursor is not None:
        return _execute(cursor)

    with get_cursor() as managed_cursor:
        return _execute(managed_cursor)
    

def get_multiple_records(
    *,
    table: str,
    criteria: dict[str, object],
    return_columns: str | list[str] = "*",
    joins: list[Join] | None = None,
    order_by: str | None = "StockCode",
    flatten: bool = False
) -> list[Row]:

    if not isinstance(return_columns, str):
        return_columns = ", ".join(return_columns)

    sql = [f"SELECT {return_columns} FROM {table}"]
    params = []
    where_clauses = []

    if joins:
        for join in joins:
            sql.append(
                f"{join.join_type} JOIN {join.table} ON {join.on}"
            )

    for col, val in criteria.items():
        if val is None:
            continue

        if isinstance(val, list):
            sub_clauses = []

            for subval in val:
                if isinstance(subval, Row):
                    subval = subval[0]

                subval = normalise_sql_value(col, subval)

                if check_if_wildcard(subval):
                    subval = substitute_wildcard(subval)
                    sub_clauses.append(f"{col} LIKE ?")
                else:
                    sub_clauses.append(f"{col} = ?")

                params.append(subval)

            if sub_clauses:
                where_clauses.append(
                    "(" + " OR ".join(sub_clauses) + ")"
                )

            continue

        if isinstance(val, Row):
            val = val[0]

        val = normalise_sql_value(col, val)

        if check_if_wildcard(val):
            val = substitute_wildcard(val)
            where_clauses.append(f"{col} LIKE ?")
        else:
            where_clauses.append(f"{col} = ?")

        params.append(val)

    if where_clauses:
        sql.append("WHERE " + " AND ".join(where_clauses))

    if order_by:
        if table in ("BomStructure", "[BomStructure+]"):
            order_by = "ParentPart"

        sql.append(f"ORDER BY {order_by}")

    final_sql = " ".join(sql)

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

    # print(f"append_single_record():")
    # print(f"Table appending to: {table}")
    # print(f"Row being appended: {row}")

    columns = list(row.keys())
    column_names = ", ".join(f"[{col}]" for col in columns)
    placeholders = ", ".join("?" for _ in columns)

    sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
    params = [row[column] for column in columns]

    with get_cursor() as cursor:
        try:
            cursor.execute(sql, params)
        except Exception:
            print("\nFAILED INSERT")
            print(sql)

            for col, val in zip(columns, params):
                print(f"{col}: {val!r} ({type(val)})")

            raise


def append_multiple_records(
    *,
    table: str,
    rows: Sequence[dict[str, object]]
) -> None:
    for i, row in enumerate(rows):
        if row.keys() != rows[0].keys():
            # print("Row 0 keys:")
            # print(set(rows[0].keys()))

            # print(f"Row {i} keys:")
            # print(set(row.keys()))

            # print("Missing from this row:")
            # print(set(rows[0].keys()) - set(row.keys()))

            # print("Extra in this row:")
            # print(set(row.keys()) - set(rows[0].keys()))

            raise ValueError(f"Row {i} has different columns to row 0")

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

    if not update_data:
        return

    set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
    where_clause, where_params = _build_where_clause(criteria)

    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    params = list(update_data.values()) + where_params

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

    where_parts = []
    params = []

    for col, val in criteria.items():

        if isinstance(val, str):
            wildcarded_val = substitute_wildcard(val)

            # If substitution changed it, or it already contains SQL wildcards
            if wildcarded_val != val or "%" in wildcarded_val or "_" in wildcarded_val:
                where_parts.append(f"{col} LIKE ?")
            else:
                where_parts.append(f"{col} = ?")

            params.append(wildcarded_val)

        else:
            where_parts.append(f"{col} = ?")
            params.append(val)

    where_clause = " AND ".join(where_parts)

    sql = f"DELETE FROM {table} WHERE {where_clause}"

    print(sql)
    print(params)

    with get_cursor() as cursor:
        cursor.execute(sql, tuple(params))
        cursor.connection.commit()


def shift_unique_sequence(
    *,
    table: str,
    sequence_column: str,
    criteria: dict[str, Any],
    delta: int,
) -> None:
    """
    Safely shifts values in a uniquely constrained sequence column.

    Updates are performed in an order that avoids temporary unique index
    violations when moving sequential values.

    For positive deltas, records are updated from highest to lowest value.
    For negative deltas, records are updated from lowest to highest value.

    All updates are executed within a single transaction. If any update
    fails, all changes are rolled back.

    Args:
        table:
            Name of the database table containing the sequence column.

        sequence_column:
            Name of the unique sequence column to shift.

        criteria:
            Dictionary of criteria used to select rows for shifting.
            Supports all operators accepted by ``_build_where_clause()``.

            Comparison operators may be specified as tuples:

                {
                    "StockCode": "FKKH2341",
                    "Route": "0",
                    "Operation": (">", 2),
                }

        delta:
            Amount by which to shift matching sequence values.

            Positive values increase the sequence.
            Negative values decrease the sequence.
            A value of zero performs no action.

    Raises:
        Exception:
            Re-raises any exception encountered during the update after
            rolling back the transaction.

    Examples:
        Insert a new operation at position 3 by shifting existing
        operations up by one:

            shift_unique_sequence(
                table="BomOperations",
                sequence_column="Operation",
                criteria={
                    "StockCode": "FKKH2341",
                    "Route": "0",
                    "Operation": (">=", 3),
                },
                delta=1,
            )

        Remove operation 3 and close the gap:

            shift_unique_sequence(
                table="BomOperations",
                sequence_column="Operation",
                criteria={
                    "StockCode": "FKKH2341",
                    "Route": "0",
                    "Operation": (">", 3),
                },
                delta=-1,
            )
    """
    if delta == 0:
        return

    order_direction = "DESC" if delta > 0 else "ASC"

    where_clause, params = _build_where_clause(criteria)

    select_sql = (
        f"SELECT {sequence_column} "
        f"FROM {table} "
        f"WHERE {where_clause} "
        f"ORDER BY {sequence_column} {order_direction}"
    )

    base_criteria = {
        col: val
        for col, val in criteria.items()
        if col != sequence_column
    }

    with get_cursor() as cursor:
        try:
            cursor.execute(select_sql, params)
            sequence_values = [row[0] for row in cursor.fetchall()]

            for old_value in sequence_values:
                new_value = old_value + delta

                update_criteria = {
                    **base_criteria,
                    sequence_column: old_value,
                }

                update_where_clause, update_params = _build_where_clause(update_criteria)

                update_sql = (
                    f"UPDATE {table} "
                    f"SET {sequence_column} = ? "
                    f"WHERE {update_where_clause}"
                )

                cursor.execute(update_sql, [new_value, *update_params])

            cursor.connection.commit()

        except Exception:
            cursor.connection.rollback()
            raise