# Checks if there is a wildcard in the criteria value
def check_if_wildcard(criterion: str) -> bool: 
    if "%" in criterion or "*" in criterion or "#" in criterion or "?" in criterion or "_" in criterion:
        return True
    else:
        return False