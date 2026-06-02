TEXT_FIELDS = {
    "Route",
    "StockCode",
    "ParentPart",
    "Component",
    "Warehouse",
    "Operation",
}

# Substitutes invalied wildcard characters for valid T-SQL equivalents
def substitute_wildcard(criterion: str) -> str:
    return criterion.replace("*", "%").replace("?", "_").replace("#", "[0-9]")

def normalise_sql_value(col: str, val):
    if val is None:
        return None

    if col in TEXT_FIELDS:
        return str(val).strip()

    return val