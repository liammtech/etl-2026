from tools.sql import update_records, get_single_record, get_multiple_records
from tools.validation import check_if_in_table

# Membrane Pressed - Standard
def memp_std_single(stock_code: str):
    bom_records_exist = check_if_in_table(
        stock_code=stock_code,
        table="BomStructure",
        sql_getter_func=get_multiple_records()
    )

    print(bom_records_exist)