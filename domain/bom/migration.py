import db.sql as sql
from tools.utils.data_utils import row_to_dict
from validation.general_validation import check_if_in_table

def copy_bomops_to_new_route(
    *,
    source_stock_code: str, 
    source_route: str,
    dest_stock_code: str = None,
    dest_route: str
) -> None:
    """
    Copy BomOperations and BomStructure records for a given parent stock code and route,
    to a new route for the same parent code (or optionally, a new parent code).

    Args:
        source_stock_code: the parent code from which to copy routing and BOM records from
        source_route: the particular BOM route to copy records from
        dest_stock_code (optional): to use if copying to a new/different stock code
        dest_route: the route to be copied to
    """
    source_route = str(source_route).strip()
    dest_route = str(dest_route).strip()

    if dest_stock_code is None:
        dest_stock_code = source_stock_code

    ops_exist_in_destination = check_if_in_table(
        key_field="StockCode",
        key_value=dest_stock_code,
        table="BomOperations",
        route=dest_route,
        sql_getter_func=sql.get_multiple_records
    )

    swap_flag = False

    if ops_exist_in_destination:
        print(
            f"Records present in destination Route {dest_route} structure & routing. "
            "Do you want to [O]verwrite, [S]wap, or [T]erminate?"
        )

        while True:
            user_choice = input().lower()

            if user_choice not in ["o", "s", "t", "overwrite", "swap", "terminate"]:
                print("Please select a valid option: [O]verwrite, [S]wap, or [T]erminate")
                continue

            break

        match user_choice:
            case "o" | "overwrite":
                print("Overwriting previous route...")
                sql.delete_records(
                    table="BomOperations",
                    criteria={"StockCode": dest_stock_code, "Route": dest_route}
                )
                sql.delete_records(
                    table="BomStructure",
                    criteria={"ParentPart": dest_stock_code, "Route": dest_route}
                )

            case "s" | "swap":
                sql.update_records(
                    table="BomOperations",
                    criteria={"StockCode": dest_stock_code, "Route": dest_route},
                    update_data={"Route": "XX"}
                )
                sql.update_records(
                    table="BomStructure",
                    criteria={"ParentPart": dest_stock_code, "Route": dest_route},
                    update_data={"Route": "XX"}
                )
                swap_flag = True

            case "t" | "terminate":
                print("Terminating.")
                return

    ops_rows = sql.get_multiple_records(
        table="BomOperations",
        criteria={
            "StockCode": source_stock_code,
            "Route": source_route,
        },
        order_by="Operation"
    )

    ops_rows = [row_to_dict(row) for row in ops_rows]

    for row in ops_rows:
        row["StockCode"] = dest_stock_code
        row["Route"] = dest_route

    sql.append_multiple_records(
        table="BomOperations",
        rows=ops_rows
    )

    bom_rows = sql.get_multiple_records(
    table="BomStructure",
    criteria={
        "ParentPart": source_stock_code,
        "Route": source_route,
    },
    order_by="SequenceNum"
)

    bom_rows = [row_to_dict(row) for row in bom_rows]

    for row in bom_rows:
        row["ParentPart"] = dest_stock_code
        row["Route"] = dest_route

    sql.append_multiple_records(
        table="BomStructure",
        rows=bom_rows
    )

    if swap_flag:
        sql.update_records(
            table="BomOperations",
            criteria={"StockCode": source_stock_code, "Route": source_route},
            update_data={"Route": dest_route}
        )
        sql.update_records(
            table="BomOperations",
            criteria={"StockCode": dest_stock_code, "Route": "XX"},
            update_data={"Route": source_route}
        )

        sql.update_records(
            table="BomStructure",
            criteria={"ParentPart": source_stock_code, "Route": source_route},
            update_data={"Route": dest_route}
        )
        sql.update_records(
            table="BomStructure",
            criteria={"ParentPart": dest_stock_code, "Route": "XX"},
            update_data={"Route": source_route}
        )

    # FUNCTION NOT FINISHED


def move_ops_to_new_route(
    *,
    source_route: str,
    source_stock_code: str, 
    dest_route: str,
    dest_stock_code: str = None
):
    """
    Copy BomOperations (not BomStructure) records to new route or parent stock code
    """
    if dest_stock_code == None:
        dest_stock_code = source_stock_code

    ops_exist_in_destination = check_if_in_table(
        stock_code=dest_stock_code,
        table="BomOperations",
        route=dest_route,
        sql_getter_func=sql.get_multiple_records
    )

    if ops_exist_in_destination:
        print("Records present in destination Route {route} structure & routing" \
              "Do you want to [O]verwrite, [S]wap, or [T]erminate?")
        
        user_choice = None

        while True:
            user_choice = input().lower()

            if user_choice not in ["o", "s", "t", "overwrite", "swap", "terminate"]:
                print("Please select a valid option: [O]verwrite, [S]wap, or [T]erminate")
                continue
            else:
                break

        match user_choice:
            case "o" | "overwrite":
                pass
            case "s" | "swap":
                pass
            case "t" | "terminate":
                print("Terminating.")
                return
            
        # FUNCTION NOT FINISHED


def delete_ops_from_route(
    *,
    route: str = "*",
    stock_code: str, 
) -> None:
    sql.delete_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": route
        }
    )


def delete_bom_from_route(
    *,
    route: str = "*",
    stock_code: str, 
) -> None:
    sql.delete_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code,
            "Route": route
        }
    )


def delete_bom_ops_from_route(
    *,
    route: str = "*",
    stock_code: str, 
) -> None:
    delete_ops_from_route(route=route, stock_code=stock_code)
    delete_bom_from_route(route=route, stock_code=stock_code)
