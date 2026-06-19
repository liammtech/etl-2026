import db.sql as sql

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
    
    # door_range = [item for sublist in door_range_result for item in sublist]
    door_range = ["BPHKNCUP64SS","BPHKNDH96SS","BPHKNKNOSS","BPHKNCUP64MB","BPHKNDH96MB","BPHKNKNOMB","BPHKNCUP64AB","BPHKNDH96AB","BPHKNKNOAB","BPHPOLKNOBLN","BPHPOLCUP76BLN","BPHHENKNOPC","BPHHENDH96PC","BPHHENKNOSS","BPHHENDH96SS","FITT15BASE","FITT15WALL","FITT15TOWER","FITT15LRDSHELF","FITT15APPSHELF","FITT15BUOVEN","FITT15SHELF","FITT15HINGEPR","BSTOR0075","BSTOR0076","BSTOR0077","BDTC15TRAY500","BDTC15TRAY600","BDTC15TRAY800"]

    for sku in door_range:
        reset_mrp(sku)