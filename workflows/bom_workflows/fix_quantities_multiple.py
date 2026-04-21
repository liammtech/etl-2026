from tools.sql import update_records, get_single_record, get_multiple_records
from workflows.bom_workflows.fix_quantities import memp_std_single, lldr_std_single, jayl_std_single

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
    # door_range = ["MEMP-PTYPE48","MEMP-PTYPE49","MEMP-PTYPE50","MEMP-PTYPE51","MEMP-PTYPE52","MEMP-PTYPE53","MEMP-PTYPE54","MEMP-PTYPE55","MEMP-PTYPE56","MEMP-PTYPE57","MEMP-PTYPE58","MEMP-PTYPE59","MEMP-PTYPE60","MEMP-PTYPE61","MEMP-PTYPE62","MEMP-PTYPE63","MEMP-PTYPE64","MEMP-PTYPE65","MEMP-PTYPE66","MEMP-PTYPE67","MEMP-PTYPE68","MEMP-PTYPE69","MEMP-PTYPE70","MEMP-PTYPE71","MEMP-PTYPE72","MEMP-PTYPE73","MEMP-PTYPE74","MEMP-PTYPE75","MEMP-PTYPE76"]

    for sku in door_range:
        memp_std_single(sku)

def lldr_std_range(stock_code: str):

    door_range = get_multiple_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code,
        },
        return_columns=[
            "StockCode"
        ]
    )
    
    print(f"Door range result is {door_range}")
    door_range = [item for sublist in door_range for item in sublist]
    # door_range = ["MEMP-PTYPE48","MEMP-PTYPE49","MEMP-PTYPE50","MEMP-PTYPE51","MEMP-PTYPE52","MEMP-PTYPE53","MEMP-PTYPE54","MEMP-PTYPE55","MEMP-PTYPE56","MEMP-PTYPE57","MEMP-PTYPE58","MEMP-PTYPE59","MEMP-PTYPE60","MEMP-PTYPE61","MEMP-PTYPE62","MEMP-PTYPE63","MEMP-PTYPE64","MEMP-PTYPE65","MEMP-PTYPE66","MEMP-PTYPE67","MEMP-PTYPE68","MEMP-PTYPE69","MEMP-PTYPE70","MEMP-PTYPE71","MEMP-PTYPE72","MEMP-PTYPE73","MEMP-PTYPE74","MEMP-PTYPE75","MEMP-PTYPE76"]

    for sku in door_range:
        lldr_std_single(sku)

def jayl_std_range(stock_code: str):

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
    # door_range = ["MEMP-PTYPE48","MEMP-PTYPE49","MEMP-PTYPE50","MEMP-PTYPE51","MEMP-PTYPE52","MEMP-PTYPE53","MEMP-PTYPE54","MEMP-PTYPE55","MEMP-PTYPE56","MEMP-PTYPE57","MEMP-PTYPE58","MEMP-PTYPE59","MEMP-PTYPE60","MEMP-PTYPE61","MEMP-PTYPE62","MEMP-PTYPE63","MEMP-PTYPE64","MEMP-PTYPE65","MEMP-PTYPE66","MEMP-PTYPE67","MEMP-PTYPE68","MEMP-PTYPE69","MEMP-PTYPE70","MEMP-PTYPE71","MEMP-PTYPE72","MEMP-PTYPE73","MEMP-PTYPE74","MEMP-PTYPE75","MEMP-PTYPE76"]

    for sku in door_range:
        jayl_std_single(sku)