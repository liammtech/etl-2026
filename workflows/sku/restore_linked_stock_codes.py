import db.sql as sql
from workflows.bom.routings import create_std_sales_code_ops, create_std_drilled_sales_ops, create_std_sales_code_bom
from domain.bom.migration import delete_bom_ops_from_route

def restore_linked_sku(stock_code: str):
    pass

    # Get size of SKU
    sku_height, sku_width = sql.get_single_record(
        table="zInvExtra",
        criteria={
            "StockCode": stock_code
        },
        return_columns=["Height", "Width"]
    )

    sku_height = int(sku_height)
    sku_width = int(sku_width)

    # Get prefix

    prefix_chars = []

    for char in stock_code:
        print(f"Current character: {char}")
        if char.isnumeric():
            print("Numeric value reached, breaking")
            break
        else:
            prefix_chars.append(char)

    prefix = "".join(prefix_chars)

    print(prefix)


    # Convert "SQ"s into Firbeck:

    lldr_flag = False

    if "PJ" in prefix and prefix[-2:] == "SQ":
        prefix = prefix[:-2].replace("PJ", "PF")
        lldr_flag = True

    print(prefix)


    # Get the linked stock code

    sql_sku = prefix + "###"

    print(sql_sku)

    linked_sku = sql.get_single_record(
        table="zInvExtra",
        criteria={
            "StockCode": sql_sku,
            "Height": sku_height,
            "Width": sku_width
        },
        return_columns=["StockCode"],
        flatten=True
    )

    print(f"\n\n======= Linked_sku type is {type(linked_sku)} =========\n\n")

    delete_bom_ops_from_route(stock_code=stock_code)

    # Build new Operations

    create_std_sales_code_ops(
        stock_code=stock_code,
        route="0"
    )

    create_std_sales_code_ops(
        stock_code=stock_code,
        route="5"
    )

    if lldr_flag:
        create_std_sales_code_ops(
            stock_code=stock_code,
            route="6"
        )
    else:
        create_std_drilled_sales_ops(
            stock_code=stock_code,
            route="6"
        )

    # Build new BOMs

    create_std_sales_code_bom(
        parent_part=stock_code,
        component=linked_sku,
        route=0
    )

    create_std_sales_code_bom(
        parent_part=stock_code,
        component=linked_sku,
        route=5
    )

    create_std_sales_code_bom(
        parent_part=stock_code,
        component=linked_sku,
        route=6
    )

    # update linked stock code

    sql.update_records(
        table="zInvExtra",
        criteria={
            "StockCode": stock_code
        },
        update_data={
            "LinkedStockCode": linked_sku
        }
    )

    # Remove MTO from LongDesc

    sql.update_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        update_data={
            "LongDesc": ""
        }
    )


def restore_linked_skus_range():

    codes_to_restore = ["PJMRG1245X296","PJMRG1245X396","PJMRG1245X496","PJMRG1245X596","PJMRG140X296","PJMRG140X396","PJMRG140X446","PJMRG140X496","PJMRG140X596","PJMRG140X796","PJMRG140X896","PJMRG140X996","PJMRG175X396","PJMRG175X496","PJMRG175X596","PJMRG283X496","PJMRG283X596","PJMRG283X796","PJMRG283X896","PJMRG283X996","PJMRG355X496","PJMRG355X596","PJMRG355X796","PJMRG355X896","PJMRG355X996","PJMRG450X396","PJMRG450X596","PJMRG490X596","PJMRG570X296","PJMRG570X396","PJMRG570X446","PJMRG570X496","PJMRG570X596","PJMRG645X596","PJMRG715X146","PJMRG715X236","PJMRG715X296","PJMRG715X346","PJMRG715X396","PJMRG715X446","PJMRG715X496","PJMRG715X596","PJMRG895X236","PJMRG895X296","PJMRG895X396","PJMRG895X496","PJMRG895X596","PJMRG980X596","PJMRGSQ110X596"]

    for code in codes_to_restore:
        restore_linked_sku(stock_code=code)