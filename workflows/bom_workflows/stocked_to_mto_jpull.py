from tools.sql import get_multiple_records, get_single_record, delete_records, update_records, append_multiple_records, append_single_record
from tools.bom_tools.bom_organisation import defrag_routing, get_next_op_number
from validation.general_validation import check_if_in_table
from tools.row_builders import build_single_bomstructure_row as build_bom_row, build_single_bomoperations_row as build_op_row
from pprint import pprint

'''
1. Park current route 0 BOM in alternate route "A"
2. Copy BOM from subcomponent/linked item
3. Replace first op with DSAWC
4. Remove PK9* layflat material
5. Re-assign B0167/* packing piece to DJSHAP op (op 4)
6. Remove DSHRIN op
7. Add in PK0170 label to op 1 (non-kit issue)
8. Add standard PICK/CHK/PACK/DESP op chain to end of current ops
9. Copy this whole BOM/op structure to route 5 (supplant previous route)
10. Copy this whole BOM/op structure to route 6 (supplant previous route)
11. In route 6, add "DPDRL" between DPCHK and DPPACK (op 7)
12. Change zInvExtra LinkedStockCode to point at the parent SKU itself
13. Change Parent SKU Long Description to "MTO"
14. Some of the Jayline sales codes historically had the colour in LongDesc; if so, move to end of description field
'''

def switch_jpull_stocked_to_mto(stock_code: str):

    ### 1. Park current route 0 BOM in alternate route "A"

    # Check if stock code exists
    sku_exists = check_if_in_table(
        stock_code=stock_code,
        table="InvMaster",
        sql_getter_func=get_single_record
    )

    if not sku_exists:
        print("SKU not found in InvMaster, terminating.")

    # Check if route A is free for the stock code, if not, prompt user to check, and ask if you want to overwrite, swap, or terminate
    route_a_ops_exists = check_if_in_table(
        stock_code=stock_code,
        table="BomOperations",
        route="A",
        sql_getter_func=get_multiple_records
    )

    route_a_bom_exists = check_if_in_table(
        stock_code=stock_code,
        table="BomStructure",
        route="A",
        sql_getter_func=get_multiple_records
    )

    route_swap_flag = None

    if route_a_ops_exists or route_a_bom_exists:
        print("Records present in Route A structure & routing\n" \
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
                delete_records(table="BomOperations", criteria={"StockCode": stock_code, "Route": "A"})
                delete_records(table="BomStructure", criteria={"ParentPart": stock_code, "Route": "A"})
            case "s" | "swap":
                update_records(table="BomOperations", criteria={"StockCode": stock_code, "Route": "A"}, update_data={"Route": "XX"})
                update_records(table="BomStructure", criteria={"ParentPart": stock_code, "Route": "A"}, update_data={"Route": "XX"})
                route_swap_flag = True
            case "t" | "terminate":
                print("Terminating.")
                return
            
    update_records(table="BomOperations", criteria={"StockCode": stock_code, "Route": "0"}, update_data={"Route": "A"})
    update_records(table="BomStructure", criteria={"ParentPart": stock_code, "Route": "0"}, update_data={"Route": "A"})

    ### 2. Copy BOM from subcomponent/linked item

    # Get the code for the linked item

    linked_stock_code = get_single_record(
        table="zInvExtra",
        criteria={
            "StockCode": stock_code
        },
        return_columns="LinkedStockCode",
        flatten=True
    )

    # Copy the linked item's operations

    linked_stock_code_ops = get_multiple_records(
        table="BomOperations",
        criteria={
            "StockCode": linked_stock_code,
            "Route": 0
        }
    )

    # Copy the linked item's materials

    linked_stock_code_bom = get_multiple_records(
        table="BomStructure",
        criteria={
            "ParentPart": linked_stock_code,
            "Route": 0
        }
    )

    print(linked_stock_code_bom)

    ops_cols = [col[0] for col in linked_stock_code_ops[0].cursor_description]
    ops_vals = [list(row) for row in linked_stock_code_ops]

    bom_cols = [col[0] for col in linked_stock_code_bom[0].cursor_description]
    bom_vals = [list(row) for row in linked_stock_code_bom]

    # Update the stock code

    for row in ops_vals:
        row[0] = stock_code

    for row in bom_vals:
        row[0] = stock_code

    ops_as_dicts = [dict(zip(ops_cols, row)) for row in ops_vals]
    bom_as_dicts = [dict(zip(bom_cols, row)) for row in bom_vals]

    # Post back in 

    # pprint(ops_as_dicts)
    # pprint(bom_as_dicts)

    append_multiple_records(
        table="BomOperations",
        rows=ops_as_dicts
    )

    append_multiple_records(
        table="BomStructure",
        rows=bom_as_dicts 
    )

    ### 3. Replace first op with DSAWC    
    
    defrag_routing(
        stock_code=stock_code,
        route=0
    )

    update_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": 0,
            "Operation": 1
        },
        update_data={
            "WorkCentre": "DSAWC"
        }
    )

    # 4. Remove PK9* layflat material

    delete_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code,
            "Route": 0,
            "Component": "PK9%"
        }
    )

    # 5. Re-assign B0167/* packing piece to DJSHAP op (op 4)

    djshap_op = get_single_record(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": 0,
            "WorkCentre": "DJSHAP"
        },
        return_columns={
            "Operation"
        },
        flatten=True
    )

    if not djshap_op:
        djshap_op = 4

    update_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code,
            "Route": 0,
            "Component": "B0167/%"
        },
        update_data={
            "OperationOffset": djshap_op
        }
    )

    # 6. Remove DSHRIN op
    
    delete_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": 0,
            "WorkCentre": "DSHRIN"
        }
    )

    # 7. Add in PK0170 label to op 1 (non-kit issue)

    PK0170_row = build_bom_row(
        parent_part=stock_code,
        component="PK0170",
        overlays={
            "QtyPer": 1,
            "QtyPerEnt": 1,
            "InclKitIssues": "N"
        }
    )

    append_single_record(
        table="BomStructure",
        row=PK0170_row
    )

    # 8. Add standard PICK/CHK/PACK/DESP op chain to end of current ops

    next_op = get_next_op_number(
        stock_code=stock_code,
        route=0
    )

    DPPICK_row = build_op_row(
        stock_code=stock_code,
        route=0,
        operation=next_op,
        work_centre="DPPICK"
    )

    DPCHK_row = build_op_row(
        stock_code=stock_code,
        route=0,
        operation=next_op + 1,
        work_centre="DPCHK",
        overlays={
            "Milestone": "N"
        }
    )

    DPPACK_row = build_op_row(
        stock_code=stock_code,
        route=0,
        operation=next_op + 2,
        work_centre="DPPACK"
    )

    DPDESP_row = build_op_row(
        stock_code=stock_code,
        route=0,
        operation=next_op + 3,
        work_centre="DPDESP"
    )

    for row in [DPPICK_row, DPCHK_row, DPPACK_row, DPDESP_row]:
        append_single_record(
            table="BomOperations",
            row=row
        )