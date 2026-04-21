import tools.sql as sql
from validation.general_validation import check_if_in_table
from typing import Literal
from collections import Counter

# This is essentially an analogue of the copy BomOperations route function in Syspro
def copy_full_bomops_route(
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

    print(f"Do ops exist in destination route: {ops_exist_in_destination}")

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