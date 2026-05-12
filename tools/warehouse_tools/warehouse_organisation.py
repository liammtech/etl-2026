from tools.sql import get_single_record

def get_default_bin(stock_code: str) -> str:
    return get_single_record(
        table="InvWarehouse",
        criteria={
            "StockCode": stock_code
        },
        return_columns={
            "DefaultBin"
        }
    )