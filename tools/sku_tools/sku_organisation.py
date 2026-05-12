from tools.sql import get_single_record

def get_sku_description(stock_code: str) -> str:
    return get_single_record(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        return_columns={
            "Description"
        }
    )

def get_sku_material_cost(stock_code: str) -> str:
    return get_single_record(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        return_columns={
            "MaterialCost"
        }
    )

def get_sku_manufacture_uom(stock_code: str) -> str:
    return get_single_record(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        return_columns={
            "ManufactureUom"
        }
    )

def get_sku_warehouse_to_use(stock_code: str) -> str:
    return get_single_record(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        return_columns={
            "ManufactureUom"
        }
    )