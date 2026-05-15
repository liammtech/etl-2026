import tools.sql as sql
from datetime import datetime
from tools.row_builders import build_invwarehouse_row

def create_invwarehouse_record(
        stock_code: str,
        warehouse: str = "DW"
    ) -> None:

    inwarehouse_row = build_invwarehouse_row(
        values={
            "StockCode": stock_code,
            "Warehouse": warehouse,
            "DefaultBin": warehouse,
            "DateWhAdded": datetime.now().date()
        }
    )

    print(inwarehouse_row)
    sql.append_single_record(
        table="InvWarehouse",
        row=inwarehouse_row
    )