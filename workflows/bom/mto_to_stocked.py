import db.sql as sql
import workflows.bom.routings.sales_codes as sales_code_ops
from workflows.bom.routings.routings_workflows import create_std_sales_code_bom
from domain.sku.analysis import determine_linked_door_component

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
    linked_sku = determine_linked_door_component(
        stock_code=stock_code
    )

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

    # 4. Insert materials

    for route in ["0", "5", "6"]:
        create_std_sales_code_bom(
            parent_part=stock_code,
            component=linked_sku,
            route=route
        )

    # 5. update zinvextra linked item

    sql.update_records(
        table="zInvExtra",
        criteria={
            "StockCode": stock_code
        },
        update_data={
            "LinkedStockCode": linked_sku
        }
    )

    # 6. Update LongDesc 
    # TODO: make this a bit more graceful, handle range colour etc. instead if desired
    # For now, just plonk in "Stocked"

    sql.update_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        update_data={
            "LongDesc": "Stocked"
        }
    )

def mto_to_stocked_range() -> None:
    # Paste range here:
    sales_code_range = [
        "WFDWCM283X496","WFDWCM283X596","WFDWCM283X796","WFDWCM355X496","WFDWCM355X596","WFDWCM450X596","WFDWCM490X596","WFDWCM570X396","WFDWCM570X496","WFDWCM570X596","WFDWCM715X296","WFDWCM715X396","WFDWCM715X446","WFDWCM715X496","WFDWCM715X596","WFDWCM895X596","WFDWCM1245X296","WFDWCM1245X496","WFDWCM1245X596","WFDWCM645X596","WFDWLG283X496","WFDWLG283X596","WFDWLG283X796","WFDWLG355X496","WFDWLG355X596","WFDWLG450X596","WFDWLG490X596","WFDWLG570X396","WFDWLG570X496","WFDWLG570X596","WFDWLG715X296","WFDWLG715X396","WFDWLG715X446","WFDWLG715X496","WFDWLG715X596","WFDWLG895X596","WFDWLG1245X296","WFDWLG1245X496","WFDWLG1245X596","WFDWLG645X596","WFDWSG283X496","WFDWSG283X596","WFDWSG283X796","WFDWSG355X496","WFDWSG355X596","WFDWSG450X596","WFDWSG490X596","WFDWSG570X396","WFDWSG570X496","WFDWSG570X596","WFDWSG715X296","WFDWSG715X396","WFDWSG715X446","WFDWSG715X496","WFDWSG715X596","WFDWSG895X596","WFDWSG1245X296","WFDWSG1245X496","WFDWSG1245X596","WFDWSG645X596","WFDWWH283X496","WFDWWH283X596","WFDWWH283X796","WFDWWH355X496","WFDWWH355X596","WFDWWH450X596","WFDWWH490X596","WFDWWH570X396","WFDWWH570X496","WFDWWH570X596","WFDWWH715X296","WFDWWH715X396","WFDWWH715X446","WFDWWH715X496","WFDWWH715X596","WFDWWH895X596","WFDWWH1245X296","WFDWWH1245X496","WFDWWH1245X596","WFDWWH645X596"
    ]

    for code in sales_code_range:
        mto_to_stocked(stock_code=code)