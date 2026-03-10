from collections.abc import Callable

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
    
    records_exist = sql_getter_func(
        criteria={"StockCode": stock_code},
        table=table
    )

    if records_exist:
        print(f"Records exist for stock code {stock_code} in table {table}: continuing...")
        return True
    else:
        print(f"No records exist for stock code {stock_code} in table {table}: continuing...")
        return False

