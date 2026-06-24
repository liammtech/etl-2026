import db.sql as sql
from datetime import datetime
import records.inventory as inventory
import records.bom as bom


def create_invwarehouse_record(
    stock_code: str,
    warehouse: str = "DW"
) -> None:

    invwarehouse_row = inventory.build_invwarehouse_row(
        values={
            "StockCode": stock_code,
            "Warehouse": warehouse,
            "DefaultBin": warehouse,
            "DateWhAdded": datetime.now().date()
        }
    )

    sql.append_single_record(
        table="InvWarehouse",
        row=invwarehouse_row
    )



def create_invwarehouse_record_range(stock_code: str):
    
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
    door_range = ["KKHKNCUP64SS","KKHKNDH96SS","KKHKNKNOSS","KKHKNCUP64MB","KKHKNDH96MB","KKHKNKNOMB","KKHKNCUP64AB","KKHKNDH96AB","KKHKNKNOAB","KKHPOLKNOBLN","KKHPOLCUP76BLN","KKHHENKNOPC","KKHHENDH96PC","KKHHENKNOSS","KKHHENDH96SS"]

    for sku in door_range:
        create_invwarehouse_record(stock_code=sku)
