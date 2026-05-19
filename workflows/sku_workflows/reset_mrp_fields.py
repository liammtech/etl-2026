import tools.sql as sql

def reset_mrp(stock_code: str) -> None:

    sql.update_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        update_data={
            "Planner": "NEW",
            "BuyingRule": "Q",
            "Buyer": "NEW",
            "LeadTime": 0,
            "ManufLeadTime": 0,
            "Ebq": 1,
            "PanSize": 0,
            "ComponentCount": 0,
            "MaterialCost": 0
        }
    )

    sql.update_records(
        table="[InvMaster+]",
        criteria={
            "StockCode": stock_code
        },
        update_data={
            "Planner2": "NEW",
            "Planner3": "NEW",
            "BaRangeName": " ",
            "RouteToMarket": " "
        }
    )

    sql.update_records(
        table="[InvWarehouse]",
        criteria={
            "StockCode": stock_code
        },
        update_data={
            "MaterialCost": 0,
            "DefaultBin": "DW"
        }
    )

def reset_mrp_range(stock_code: str):    

    door_range_result = sql.get_multiple_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code,
        },
        return_columns=[
            "StockCode"
        ]
    )
    
    door_range = [item for sublist in door_range_result for item in sublist]
    # door_range = ["FFPDLO006","FFPDLO007","FFPDLO008","FFPDLO009","FFPDLO010","FFPDLO011","FFPDMW006","FFPDMW007","FFPDMW008","FFPDMW009","FFPDMW010","FFPDMW011","FFPDUO006","FFPDUO007","FFPDUO008","FFPDUO009","FFPDUO010","FFPDUO011","FFPRMC006","FFPRMC007","FFPRMC008","FFPRMC009","FFPRMC010","FFPRMC011","FFPRLO006","FFPRLO007","FFPRLO008","FFPRLO009","FFPRLO010","FFPRLO011","FFPRUO006","FFPRUO007","FFPRUO008","FFPRUO009","FFPRUO010","FFPRUO011"]

    for sku in door_range:
        reset_mrp(sku)