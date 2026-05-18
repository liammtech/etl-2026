from tools.sql import get_single_record

def get_default_bin(stock_code: str, warehouse: str) -> str:
    default_bin = get_single_record(
        table="InvWarehouse",
        criteria={
            "StockCode": stock_code,
            "Warehouse": warehouse
        },
        return_columns={
            "DefaultBin"
        }
    )

    return default_bin[0]