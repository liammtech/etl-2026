import db.sql as sql
from tools.utils.data_utils import row_to_dict
from validation.general_validation import check_if_in_table
from typing import Literal
from tools.row_builders import build_bomoperations_row

from collections import Counter

# This is essentially an analogue of the copy BomOperations route function in Syspro
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


def specify_lldr_edged_sides(
    *,
    no_edged_sides: Literal[1, 2, 3, 4, "DEBAN1", "DEBAN2", "DEBAN3", "DEBAN4"] = 4,
    stock_code: str = "STOCK-CODE"
) -> dict:
    
    print(f"Case for edging switch statement is {no_edged_sides}")
    sides_edged = {"H": 0, "W": 0}

    match no_edged_sides:

        case 1 | "DEBAN1":
            while True:
                res = input(f"DEBAN1: Which side to be edged for {stock_code}? (H/W): ").strip().upper()
                if res in ("H", "W"):
                    break
                print("Please enter H (Height) or W (Width)")
            sides_edged[res] += 1

        case 2 | "DEBAN2":
            while True:
                res = input(f"DEBAN2: Are sides to be edged along height or width for {stock_code}? (H/W): ").strip().upper()
                if res in ("H", "W"):
                    break
                print("Please enter H (Height) or W (Width)")
            sides_edged[res] += 2

        case 3 | "DEBAN3":
            while True:
                res = input(f"DEBAN3: Which side to be left un-edged for {stock_code}? (H/W): ").strip().upper()
                if res in ("H", "W"):
                    break
                print("Please enter H (Height) or W (Width)")
            other = next(k for k in sides_edged if k != res)
            sides_edged[res] += 1
            sides_edged[other] += 2

        case 4 | "DEBAN4":
            sides_edged = {"H": 2, "W": 2}

    print(sides_edged)
    return sides_edged


def specify_jayl_edged_sides(
    *,
    no_edged_sides: Literal[2, 3, "DEBAN2", "DEBAN3"] = 2,
    stock_code: str,
    jpull_direction: str = "Horizontal"
) -> dict:
    
    print(f"Case for edging switch statement is {no_edged_sides}")
    sides_edged = {"H": 0, "W": 0}

    if jpull_direction == "Vertical":
        match no_edged_sides:

            case 2 | "DEBAN2":
                sides_edged["W"] = 2

            case 3 | "DEBAN3":
                sides_edged["W"] = 2
                sides_edged["H"] = 1

    else:
        match no_edged_sides:

            case 2 | "DEBAN2":
                sides_edged["H"] = 2

            case 3 | "DEBAN3":
                sides_edged["H"] = 2
                sides_edged["W"] = 1

    return sides_edged


def get_range_modal_component(
    *,
    stock_code_prefix: str,
    component_prefixes: str | list[str]
) -> str:
    all_components = sql.get_multiple_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code_prefix,
            "Component": component_prefixes
        },
        return_columns=["Component"]
    )

    all_components = [item for sublist in all_components for item in sublist]
    components_count = Counter(list(all_components))
    modal_component = components_count.most_common()[0][0]

    print(modal_component)
    return modal_component


def build_op_num_mapping(op_nums: list[int]) -> dict[int, int]:
    unique_sorted = sorted(set(op_nums))
    return {old: new for new, old in enumerate(unique_sorted, start=1)}


def defrag_routing(
    stock_code: str,
    route: str = "*"
):
    # One stock code, in one route, at a time
    
    # 1. Get list of op numbers
    route = str(route).strip()

    print(F"DEFRAGGING FOR ROUTE: {route}")

    op_nums = sql.get_multiple_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": route
        },
        return_columns={
            "Operation"
        }
    )

    print("Hit heeeeeeeeeeeeeeeere?")
    op_nums = [int(i) for list in op_nums for i in list]
    op_nums.sort()

    mapping = build_op_num_mapping(op_nums=op_nums)

    for old_op, new_op in mapping.items():
        if old_op == new_op:
            continue

        sql.update_records(
            table="BomOperations",
            criteria={
                "StockCode": stock_code,
                "Route": route,
                "Operation": old_op
            },
            update_data={"Operation": new_op}
        )

        sql.update_records(
            table="[BomOperations+]",
            criteria={
                "StockCode": stock_code,
                "Route": route,
                "Operation": old_op
            },
            update_data={"Operation": new_op}
        )

        sql.update_records(
            table="BomStructure",
            criteria={
                "ParentPart": stock_code,
                "Route": route,
                "OperationOffset": old_op
            },
            update_data={"OperationOffset": new_op}
        )


def defrag_routing_multiple(
    range: list
) -> None:
    for i in range: 
        defrag_routing(i)


def get_next_op_number(
    stock_code: str,
    route: str = 0
) -> int:
    op_nums = sql.get_multiple_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": route
        },
        return_columns={
            "Operation"
        }
    )

    op_nums = [int(i) for list in op_nums for i in list]
    op_nums.sort()

    next_op = op_nums[-1] + 1

    return next_op


def check_if_work_centre_in_routing(
    stock_code: str,
    route: str,
    work_centre: str
) -> bool:
    """
    Check if a given work centre is present within the operations list for
    a stock code in a particular route.

    Args:
        stock_code: The stock code to check
        route: The operations routing to check
        work_centre: The work centre being checked to see if it is present

    Returns:
        bool: True if work centre is present, otherwise False
    """

    query_result = sql.get_single_record(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": route,
            "WorkCentre": work_centre
        }
    )

    return True if query_result else False


def insert_operation(
    stock_code: str,
    route: str,
    work_centre: str,
    after_work_centre: str | None = None,
    op_number: int | None = None
) -> None:
    '''
    Inserts an operation at a specified position. Specify either the work
    centre to place the new op after, or a specified position (mutually exclusive).

    Note: If using after_work_centre and there are multiple instances of the same work centre
    already existing, it will insert after the first instance.

    Args:
        stock_code: The stock code to receive the new operation
        route: The route to insert the new operation into
        work_centre: The work centre to be inserted
        after_work_centre: Mutually exclusive with op_number. The work centre to follow with the new operation
        op_number: Mutually exclusive with after_work_centre. The operation number to place the new operation at

    Returns:
        None. Inserts a new operation as specified, incrementing any subsequent lines' op numbers by 1

    '''

    if (after_work_centre is None) == (op_number is None):
        raise ValueError("Exactly one of these parameters must be supplied: after_work_centre or op_number")
    
    prev_op = None

    if after_work_centre:
        prev_op = sql.get_single_record(
            table="BomOperations",
            criteria={
                "StockCode": stock_code,
                "Route": route,
                "WorkCentre": after_work_centre
            },
            return_columns=["Operation"],
            flatten=True
        )

        if not prev_op:
            print(f"{stock_code}: no {after_work_centre} work centre found in route {route}, skipping...")
            return

        op_number = prev_op + 1

    shift_from = op_number

    sql.shift_unique_sequence(
        table="BomOperations",
        sequence_column="Operation",
        criteria={
            "StockCode": stock_code,
            "Route": route,
            "Operation": (">=", shift_from),
        },
        delta=1
    )
        
    op_row = build_bomoperations_row(
        stock_code=stock_code,
        route=route,
        operation=op_number,
        work_centre=work_centre
    )

    sql.append_single_record(
        table="BomOperations",
        row=op_row
    )