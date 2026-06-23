from db.sql import update_records, get_single_record, get_multiple_records
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
    
    # door_range = [item for sublist in door_range_result for item in sublist]
    door_range = ["PFMW127","PFMCB127","PFMCM127","PFMDG127","PFMG127","PFMSG127","ORAGC127","ORAGG127","ORAGW127","ORAMA127","ORAMZ127","ORAMQ127","ORAMC127","ORAMG127","ORAMW127"]

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
    # door_range = [item for sublist in door_range for item in sublist]
    door_range = ["PFMW128","PFMCB128","PFMCM128","PFMDG128","PFMG128","PFMSG128","ORAGC128","ORAGG128","ORAGW128","ORAMA128","ORAMZ128","ORAMQ128","ORAMC128","ORAMG128","ORAMW128"]

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
    
    # door_range = [item for sublist in door_range_result for item in sublist]
    door_range = ["FUJGCM001","FUJGCM002","FUJGCM006","FUJGDG001","FUJGDG002","FUJGDG006","FUJGLG001","FUJGLG002","FUJGLG006","FUJGW001","FUJGW002","FUJGW006"]

    for sku in door_range:
        jayl_std_single(sku)