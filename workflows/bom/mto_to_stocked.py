import db.sql as sql
import workflows.bom.routings.sales_codes as sales_code_ops


'''
This is for any standard pronto door code

0. Check the code exists - if not, terminate
1. Delete all ops and materials
2. Determine linked item
3. Insert ops for routes 0, 5, 6 (6 is drilled)
4. Insert linked item and label for routes 0, 5, 6
5. Update zInvExtra.LinkedStockCode
6. Update LongDesc
'''

def mto_to_stocked(stock_code: str) -> None:
    # 0. Check code exists
    code_to_change = sql.get_single_record(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        return_columns=["StockCode"]
    )

    if not code_to_change:
        raise ValueError(f"No stock code {stock_code} found in InvMaster, terminating. \n")
    
    # 1. Delete ops and materials
    sql.delete_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code
        }
    )

    sql.delete_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code
        }
    )

    sql.delete_records(
        table="[BomOperations+]",
        criteria={
            "StockCode": stock_code
        }
    )

    sql.delete_records(
        table="[BomStructure+]",
        criteria={
            "ParentPart": stock_code
        }
    )

    # 2. Determine linked item

    # 3. Insert ops

    for route in ["0", "5"]:
        sales_code_ops.create_std_sales_code_ops(
            stock_code=stock_code,
            route=route
        )

    sales_code_ops.create_std_drilled_sales_code_ops(
        stock_code=stock_code,
        route="6"
    )