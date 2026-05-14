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
            "DefaultBin": "NEW"
        }
    )