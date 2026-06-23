from typing import Literal, NamedTuple
from pyodbc import Row

VALID_OPS = {"=", "!=", "<>", ">", ">=", "<", "<=", "LIKE", "NOT LIKE"}


TEXT_FIELDS = {
    "Route",
    "StockCode",
    "ParentPart",
    "Component",
    "Warehouse",
    "Operation",
}

class Join(NamedTuple):
    table: str
    on: str
    join_type: Literal["INNER", "LEFT", "RIGHT"] = "INNER"


def build_where_clause(
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


# Substitutes invalied wildcard characters for valid T-SQL equivalents
def substitute_wildcard(criterion: str) -> str:
    return criterion.replace("*", "%").replace("?", "_").replace("#", "[0-9]")


def normalise_sql_value(col: str, val):
    if val is None:
        return None

    if col in TEXT_FIELDS:
        return str(val).strip()

    return val


# Checks if there is a wildcard in the criteria value
def check_if_wildcard(criterion: str) -> bool: 
    criterion = str(criterion)
    if "%" in criterion or "*" in criterion or "#" in criterion or "?" in criterion or "_" in criterion:
        return True
    else:
        return False
    

