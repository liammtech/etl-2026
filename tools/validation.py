from collections.abc import Callable
from pathlib import Path
import yaml

class RecordNotFoundError(Exception):
    """Raised when a specific record is not found in the database."""
    pass

# YAML loader and checker
def check_yaml(file_path, search_key, search_value=None):
    print(f"Checking YAML - search key : {search_key} - search val: {search_value}")
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    print(data)
    if search_key in data:
        print(f"Table '{search_key}' found")
    else:
        print("Table not found")




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
    route: str = None,
    sql_getter_func: Callable
) -> bool: 
    
    print(f"Route is {route}")
    
    if table == "BomStructure" or table == "BomStructure+":
        criteria = {"ParentPart": stock_code}
        if route == None:
            records_exist = sql_getter_func(
                criteria=criteria,
                table=table
            )
        else:
            records_exist = sql_getter_func(
                criteria=criteria,
                table=table,
                route=route
            )
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

# Check if table is in allowed tables
def check_if_table_allowed(table_name):
    config_path = Path(__file__).resolve().parents[1] / "config/validation/valid_tables.yml"
    print(config_path)
    check_yaml(config_path, table_name)
    

'''
Logic:

1. Validate that the list of materials contains (and only contains):
    - A line for a MEL* code
    - A line for GL100
    - A line for GL101
    - A line for a PV* code
    - A line for a pallet

2. We do not validate what specific materials are, that is beyond the scope of this function

3. 
'''

def check_path():
    print("Initialising")
    the_path = Path(__file__).resolve().parents[1] / "config/validation/valid_tables.yml"
    print(f"\nPath is {the_path}")