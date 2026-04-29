import tools.sql as sql
from validation.general_validation import check_if_in_table
from typing import Literal
from collections import Counter

# This is essentially an analogue of the copy BomOperations route function in Syspro
def copy_bomops_to_new_route(
    *,
    source_route: str,
    source_stock_code: str, 
    dest_route: str,
    dest_stock_code: str = None
):
    if dest_stock_code == None:
        dest_stock_code = source_stock_code

    ops_exist_in_destination = check_if_in_table(
        stock_code=dest_stock_code,
        table="BomOperations",
        route=dest_route,
        sql_getter_func=sql.get_multiple_records
    )

    swap_flag = False

    if ops_exist_in_destination:
        print(f"Records present in destination Route {dest_route} structure & routing" \
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
                print("Overwriting previous route...")
                sql.delete_records(table="BomOperations", criteria={"StockCode": dest_stock_code, "Route": dest_route})
                sql.delete_records(table="BomStructure", criteria={"ParentPart": dest_stock_code, "Route": dest_route})
            case "s" | "swap":
                sql.update_records(table="BomOperations", criteria={"StockCode": dest_stock_code, "Route": dest_route}, update_data={"Route": "XX"})
                sql.update_records(table="BomStructure", criteria={"ParentPart": dest_stock_code, "Route": dest_route}, update_data={"Route": "XX"})
                swap_flag = True
            case "t" | "terminate":
                print("Terminating.")
                return
            
    print("Did it get here")
    ops_rows = sql.get_multiple_records(
        table="BomOperations",
        criteria={
            "StockCode": source_stock_code,
            "Route": source_route
        }
    )

    bom_rows = sql.get_multiple_records(
        table="BomStructure",
        criteria={
            "ParentPart": source_stock_code,
            "Route": source_route
        }
    )

    for row in ops_rows:
        row.Route = dest_route

    for row in bom_rows:
        pass
        row.Route = dest_route

    sql.append_multiple_records(
        table="BomOperations",
        rows=ops_rows
    )

    sql.append_multiple_records(
        table="BomStructure",
        rows=bom_rows
    )

    if swap_flag:
        sql.update_records(table="BomOperations", criteria={"StockCode": dest_stock_code, "Route": "XX"}, update_data={"Route": source_route})
        sql.update_records(table="BomStructure", criteria={"ParentPart": dest_stock_code, "Route": "XX"}, update_data={"Route": source_route})

    # FUNCTION NOT FINISHED

def move_ops_to_new_route(
    *,
    source_route: str,
    source_stock_code: str, 
    dest_route: str,
    dest_stock_code: str = None
):
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
    route: str,
    stock_code: str, 
) -> None:
    pass

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
    route: str
):
    # One stock code, in one route, at a time
    
    # 1. Get list of op numbers

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
                "Route": 0,
                "Operation": old_op
            },
            update_data={"Operation": new_op}
        )

        sql.update_records(
            table="[BomOperations+]",
            criteria={
                "StockCode": stock_code,
                "Route": 0,
                "Operation": old_op
            },
            update_data={"Operation": new_op}
        )

        sql.update_records(
            table="BomStructure",
            criteria={
                "ParentPart": stock_code,
                "Route": 0,
                "OperationOffset": old_op
            },
            update_data={"OperationOffset": new_op}
        )

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