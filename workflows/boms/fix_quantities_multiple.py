from tools.sql import update_records, get_single_record, get_multiple_records
from workflows.boms.fix_quantities import memp_std_single

def memp_std_range(stock_code: str):

    door_range_result = get_multiple_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code,
        },
        return_columns=[
            "StockCode"
        ]
    )
    
    door_range = [item for sublist in door_range_result for item in sublist]

    for sku in door_range:
        memp_std_single(sku)