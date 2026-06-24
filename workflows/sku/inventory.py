import db.sql as sql
import records.inventory as inventory


def create_invmasterplus_record(
    stock_code: str
) -> None:
    
    invmasterplus_row = inventory.build_invmasterplus_row(
        values={
            "StockCode": stock_code
        }
    )

    sql.append_single_record(
        table="[InvMaster+]",
        row=invmasterplus_row
    )


def create_invmasterplus_record_range(stock_code: str):
    
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
        create_invmasterplus_record(stock_code=sku)
