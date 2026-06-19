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

        if value is None:
            continue

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
    """Fetch a single record from a database table.

    Records are filtered using the supplied criteria. Criteria handling
    supports equality matching, comparison operators, wildcard matching,
    and lists of values via ``_build_where_clause()``.

    By default, the first matching row is returned. When ``strict=True``,
    the function validates that no more than one matching row exists.

    If no external cursor is supplied, a managed cursor is created using
    ``get_cursor()``. When a cursor is provided, the query participates in
    the caller's transaction scope.

    Args:
        table: Name of the table to query.

        criteria: Mapping of column names to filter values or
            ``(operator, value)`` tuples.

        return_columns: Column or columns to return. May be supplied as
            ``"*"`` to select all columns, a comma-separated string, or
            a list of column names.

        joins: Optional sequence of JOIN definitions to include in the
            query.

        flatten: If ``True``, return the first column value directly
            instead of a ``Row`` object. Requires exactly one column to
            be returned.

        strict: If ``True``, raise a ``ValueError`` when multiple records
            match the supplied criteria.

        cursor: Optional database cursor. When provided, the query uses
            the existing cursor instead of creating a new one.

    Returns:
        A ``Row`` object containing the matching record, a single value if
        ``flatten=True``, or ``None`` if no matching record is found.

    Raises:
        ValueError: If ``criteria`` is empty.

        ValueError: If ``strict=True`` and multiple records match the
            supplied criteria.

        ValueError: If ``flatten=True`` and more than one column is
            returned.

    Examples:
        Fetch a single row:

            get_single_record(
                table="InvMaster",
                criteria={"StockCode": "FKKH2341"},
            )

        Fetch a single value:

            get_single_record(
                table="InvMaster",
                criteria={"StockCode": "FKKH2341"},
                return_columns=["Description"],
                flatten=True,
            )

        Enforce uniqueness:

            get_single_record(
                table="BomOperations",
                criteria={
                    "StockCode": "FKKH2341",
                    "Operation": 10,
                },
                strict=True,
            )

        Participate in an existing transaction:

            with get_cursor() as cursor:
                record = get_single_record(
                    table="InvMaster",
                    criteria={"StockCode": "FKKH2341"},
                    cursor=cursor,
                )
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
    flatten: bool = False,
    cursor: Cursor | None = None,
) -> list[Row] | list[object]:
    """Fetch multiple records from a database table.

    Records are filtered using the supplied criteria. Criteria handling
    supports equality matching, comparison operators, wildcard matching,
    lists of values, and explicit SQL operators via ``_build_where_clause()``.

    If no external cursor is supplied, a managed cursor is created using
    ``get_cursor()``. When a cursor is provided, the query participates in
    the caller's transaction scope.

    Results may optionally be ordered and flattened into a simple list of
    values when only a single column is required.

    Args:
        table: Name of the table to query.

        criteria: Mapping of column names to filter values, lists of values,
            or ``(operator, value)`` tuples.

        return_columns: Column or columns to return. May be supplied as
            ``"*"`` to select all columns, a comma-separated string, or
            a list of column names.

        joins: Optional sequence of JOIN definitions to include in the
            query.

        order_by: Column name to order the results by. Pass ``None`` to
            omit the ``ORDER BY`` clause.

        flatten: If ``True``, return the first column value from each row
            instead of ``Row`` objects. Requires exactly one column to be
            returned.

        cursor: Optional database cursor. When provided, the query uses
            the existing cursor instead of creating a new one.

    Returns:
        A list of ``Row`` objects containing the matching records, or a
        list of values if ``flatten=True``.

        An empty list is returned if no matching records are found.

    Raises:
        ValueError: If ``criteria`` is empty.

        ValueError: If an unsupported SQL operator is supplied.

    Examples:
        Fetch all matching rows:

            get_multiple_records(
                table="BomOperations",
                criteria={
                    "StockCode": "FKKH2341",
                    "Route": "0",
                },
            )

        Match multiple values:

            get_multiple_records(
                table="InvMaster",
                criteria={
                    "StockCode": [
                        "FKKH2341",
                        "FKKH2342",
                        "FKK?####",
                    ],
                },
            )

        Use comparison operators:

            get_multiple_records(
                table="BomOperations",
                criteria={
                    "Operation": (">", 10),
                },
            )

        Fetch a flattened list of values:

            get_multiple_records(
                table="InvMaster",
                criteria={
                    "ProductClass": "KKF",
                },
                return_columns=["StockCode"],
                flatten=True,
            )

        Participate in an existing transaction:

            with get_cursor() as cursor:
                records = get_multiple_records(
                    table="BomOperations",
                    criteria={"StockCode": "FKKH2341"},
                    cursor=cursor,
                )
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

    if order_by:
        if table in ("BomStructure", "[BomStructure+]"):
            order_by = "ParentPart"

        sql.append(f"ORDER BY {order_by}")

    final_sql = " ".join(sql)

    def _execute(active_cursor: Cursor) -> list[Row] | list[object]:
        active_cursor.execute(final_sql, params)
        rows = active_cursor.fetchall()

        if flatten:
            return [row[0] for row in rows]

        return rows

    if cursor is not None:
        return _execute(cursor)

    with get_cursor() as managed_cursor:
        return _execute(managed_cursor)
    

def append_single_record(
    *,
    table: str,
    row: dict[str, object],
    cursor: Cursor | None = None,
) -> None:
    """Insert a single row into a database table.

    Args:
        table: Name of the table to insert into.

        row: Mapping of column names to values for the new record.

        cursor: Optional database cursor. When provided, the insert uses
            the existing cursor instead of creating a new one.

    Raises:
        ValueError: If ``row`` is empty.

        pyodbc.Error: If the insert fails.
    """
    if not row:
        raise ValueError("Cannot append an empty row.")

    columns = list(row.keys())
    column_names = ", ".join(f"[{column}]" for column in columns)
    placeholders = ", ".join("?" for _ in columns)

    sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
    params = [row[column] for column in columns]

    def _execute(active_cursor: Cursor) -> None:
        try:
            active_cursor.execute(sql, params)
        except Exception:
            print("\nFAILED INSERT")
            print(sql)

            for column, value in zip(columns, params):
                print(f"{column}: {value!r} ({type(value)})")

            raise

    if cursor is not None:
        _execute(cursor)
        return

    with get_cursor() as managed_cursor:
        _execute(managed_cursor)


def append_multiple_records(
    *,
    table: str,
    rows: Sequence[dict[str, object] | Row],
    cursor: Cursor | None = None,
) -> None:
    """Insert multiple rows into a database table.

    Args:
        table: Name of the table to insert into.

        rows: Sequence of row mappings to insert. ``pyodbc.Row`` objects
            are also accepted and converted to dictionaries.

        cursor: Optional database cursor. When provided, the insert uses
            the existing cursor instead of creating a new one.

    Raises:
        ValueError: If ``rows`` is empty.

        ValueError: If rows do not all contain the same columns.

        pyodbc.Error: If the insert fails.
    """
    if not rows:
        raise ValueError("Cannot append an empty sequence of rows.")

    normalised_rows: list[dict[str, object]] = []

    for row in rows:
        if isinstance(row, Row):
            row = dict(
                zip(
                    [column[0] for column in row.cursor_description],
                    row,
                )
            )

        normalised_rows.append(row)

    first_row = normalised_rows[0]

    for index, row in enumerate(normalised_rows):
        if row.keys() != first_row.keys():
            raise ValueError(
                f"Row {index} has different columns to row 0."
            )

    excluded_keys = {
        key
        for key, value in first_row.items()
        if (
            isinstance(value, (bytes, bytearray))
            and len(value) == 8
        )
        or key.lower() == "timestamp"
    }

    columns = [
        column
        for column in first_row.keys()
        if column not in excluded_keys
    ]

    column_names = ", ".join(f"[{column}]" for column in columns)
    placeholders = ", ".join("?" for _ in columns)

    sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

    param_sets = [
        [row[column] for column in columns]
        for row in normalised_rows
    ]

    def _execute(active_cursor: Cursor) -> None:
        try:
            active_cursor.executemany(sql, param_sets)
        except Exception:
            print("\nFAILED MULTI-INSERT")
            print(sql)
            print(f"Rows attempted: {len(param_sets)}")
            print(f"Columns: {columns}")
            raise

    if cursor is not None:
        _execute(cursor)
        return

    with get_cursor() as managed_cursor:
        _execute(managed_cursor)


def update_records(
    *,
    table: str,
    criteria: dict[str, object],
    update_data: dict[str, object],
    cursor: Cursor | None = None,
    debug: bool = False,
) -> None:
    """Update records in a database table.

    Records matching ``criteria`` are updated using the values supplied in
    ``update_data``. Criteria handling is delegated to
    ``_build_where_clause()``.

    Args:
        table: Name of the table to update.

        criteria: Mapping of column names to filter values, lists of values,
            or ``(operator, value)`` tuples.

        update_data: Mapping of column names to new values.

        cursor: Optional database cursor. When provided, the update uses
            the existing cursor instead of creating a new one.

        debug: If ``True``, print the generated SQL and parameter values.

    Raises:
        ValueError: If ``update_data`` is empty.

        ValueError: If ``criteria`` is empty.

        pyodbc.Error: If the update fails.
    """
    if not update_data:
        raise ValueError("Cannot update records with empty update_data.")

    set_clause = ", ".join(
        f"[{column}] = ?"
        for column in update_data.keys()
    )

    where_clause, where_params = _build_where_clause(criteria)

    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    params = list(update_data.values()) + where_params

    if debug:
        print(sql)
        print(params)

    def _execute(active_cursor: Cursor) -> None:
        active_cursor.execute(sql, params)

    if cursor is not None:
        _execute(cursor)
        return

    with get_cursor() as managed_cursor:
        _execute(managed_cursor)


def delete_records(
    *,
    table: str,
    criteria: dict[str, object],
    cursor: Cursor | None = None,
    debug: bool = False,
) -> None:
    """Delete records from a database table.

    Records matching ``criteria`` are deleted. Criteria handling is
    delegated to ``_build_where_clause()``, so equality matching,
    wildcard matching, comparison operators, and lists of values are
    supported.

    Args:
        table: Name of the table to delete from.

        criteria: Mapping of column names to filter values, lists of values,
            or ``(operator, value)`` tuples.

        cursor: Optional database cursor. When provided, the delete uses
            the existing cursor instead of creating a new one.

        debug: If ``True``, print the generated SQL and parameter values.

    Raises:
        ValueError: If ``criteria`` is empty.

        pyodbc.Error: If the delete fails.
    """
    where_clause, params = _build_where_clause(criteria)

    sql = f"DELETE FROM {table} WHERE {where_clause}"

    if debug:
        print(sql)
        print(params)

    def _execute(active_cursor: Cursor) -> None:
        active_cursor.execute(sql, params)

    if cursor is not None:
        _execute(cursor)
        return

    with get_cursor() as managed_cursor:
        _execute(managed_cursor)


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