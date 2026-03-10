from collections.abc import Callable

class RecordNotFoundError(Exception):
    """Raised when a specific record is not found in the database."""
    pass

# Checks if there is a wildcard in the criteria value
def check_if_wildcard(criterion: str) -> bool: 
    if "%" in criterion or "*" in criterion or "#" in criterion or "?" in criterion or "_" in criterion:
        return True
    else:
        return False
    
# Checks if record exists in a table via primary key
def check_if_in_table(
    *,
    stock_code: str,
    table: str,
    sql_getter_func: Callable
) -> bool: 
    
    if table == "BomStructure" or table == "BomStructure+":
        criteria = {"ParentPart": stock_code}
    else:
        criteria = {"StockCode": stock_code}
    
    records_exist = sql_getter_func(
        criteria=criteria,
        table=table
    )

    if records_exist:
        print(f"\nRecords exist for stock code {stock_code} in table {table}: continuing...\n")
        return True
    else:
        print(f"\nNo records exist for stock code {stock_code} in table {table}: continuing...\n")
        return False

'''
Logic:

1. Validate that the list of materials contains (and only contains):
    - A line for a MEL* code
    - A line for GL100
    - A line for GL101
    - A line for a PV* code
    - A line for a pallet

2. We do not validate what specific materials are, that is beyond the scope of this function
'''