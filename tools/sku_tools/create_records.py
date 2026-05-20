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