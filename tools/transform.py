# Substitutes invalied wildcard characters for valid T-SQL equivalents
def substitute_wildcard(criterion: str) -> str:
    return criterion.replace("*", "%").replace("?", "_").replace("#", "[0-9]")