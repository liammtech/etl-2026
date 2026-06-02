import tools.sql as sql
from datetime import datetime
import tools.row_builders as row_builder

# These builders act as an interface to the row builders, that actually set up and post the table records in the format that they generally want to exist in on the system

def create_invwarehouse_record(
    stock_code: str,
    warehouse: str = "DW"
) -> None:

    invwarehouse_row = row_builder.build_invwarehouse_row(
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
    
    door_range = [item for sublist in door_range_result for item in sublist]
    # door_range = ["BPHKNCUP64SS","BPHKNDH96SS","BPHKNKNOSS","BPHKNCUP64MB","BPHKNDH96MB","BPHKNKNOMB","BPHKNCUP64AB","BPHKNDH96AB","BPHKNKNOAB","BPHPOLKNOBLN","BPHPOLCUP76BLN","BPHHENKNOPC","BPHHENDH96PC","BPHHENKNOSS","BPHHENDH96SS","FITT15BASE","FITT15WALL","FITT15TOWER","FITT15LRDSHELF","FITT15APPSHELF","FITT15BUOVEN","FITT15SHELF","FITT15HINGEPR","BSTOR0075","BSTOR0076","BSTOR0077","BDTC15TRAY500","BDTC15TRAY600","BDTC15TRAY800"]

    for sku in door_range:
        create_invwarehouse_record(stock_code=sku)



def create_invmasterplus_record(
    stock_code: str
) -> None:
    
    invmasterplus_row = row_builder.build_invmasterplus_row(
        values={
            "StockCode": stock_code
        }
    )

    sql.append_single_record(
        table="[InvMaster+]",
        row=invmasterplus_row
    )


def create_arcuststkref_record(
    
) -> None:
    pass