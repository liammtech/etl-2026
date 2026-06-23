from db.sql import get_multiple_records, get_single_record, delete_records, update_records, append_multiple_records, append_single_record
from domain.bom.migration import copy_bomops_to_new_route
from domain.bom.routing import defrag_routing, get_next_op_number
from validation.general_validation import check_if_in_table
from tools.row_builders import build_bomoperations_row, build_bomstructure_row
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
        key_field="StockCode",
        key_value=stock_code,
        table="InvMaster",
        sql_getter_func=get_single_record
    )

    if not sku_exists:
        print("SKU not found in InvMaster, terminating.")

    # Check if route A is free for the stock code, if not, prompt user to check, and ask if you want to overwrite, swap, or terminate
    route_a_ops_exists = check_if_in_table(
        key_field="StockCode",
        key_value=stock_code,
        table="BomOperations",
        route="A",
        sql_getter_func=get_multiple_records
    )

    route_a_bom_exists = check_if_in_table(
        key_field="ParentPart",
        key_value=stock_code,
        table="BomStructure",
        route="A",
        sql_getter_func=get_multiple_records
    )

    route_swap_flag = None

    if route_a_ops_exists or route_a_bom_exists:
        print("Records present in Route A structure & routing\n" \
              "Do you want to [O]verwrite or [T]erminate? (Swap not available as route 0 required)")
        
        user_choice = None

        while True:
            user_choice = input().lower()

            if user_choice not in ["o", "t", "overwrite", "terminate"]:
                print("Please select a valid option: [O]verwrite or [T]erminate")
                continue
            else:
                break

        match user_choice:
            case "o" | "overwrite":
                print("Overwriting previous route...")
                delete_records(table="BomOperations", criteria={"StockCode": stock_code, "Route": "A"})
                delete_records(table="BomStructure", criteria={"ParentPart": stock_code, "Route": "A"})
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

    if linked_stock_code == stock_code:
        print("Grabbing stuff from route 5")
        linked_stock_code_ops = get_multiple_records(
            table="BomOperations",
            criteria={
                "StockCode": linked_stock_code,
                "Route": "5"
            }
        )
    else:
        print("Grabbing stuff from route 0")
        linked_stock_code_ops = get_multiple_records(
            table="BomOperations",
            criteria={
                "StockCode": linked_stock_code,
                "Route": "0"
            }
        )

    print(f"LINKED STOCK CODE: {linked_stock_code}")
    print(f"LINKED STOCK CODE OPS: {linked_stock_code_ops}")

    # Copy the linked item's materials

    if linked_stock_code == stock_code:
        print("Grabbing stuff from route 5")
        linked_stock_code_bom = get_multiple_records(
            table="BomStructure",
            criteria={
                "ParentPart": linked_stock_code,
                "Route": "5"
            }
        )
    else:
        print("Grabbing stuff from route 0")
        linked_stock_code_bom = get_multiple_records(
            table="BomStructure",
            criteria={
                "ParentPart": linked_stock_code,
                "Route": "0"
            }
        )

    print(f"Linked stock code ops: {linked_stock_code_ops}")

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

    for row in ops_as_dicts:
        row.pop('TimeStamp', None)

    for row in bom_as_dicts:
        row.pop('TimeStamp', None)

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
        route="0"
    )

    update_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": "0",
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
            "Route": "0",
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
            "Route": "0",
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
            "Route": "0",
            "WorkCentre": "DSHRIN"
        }
    )


    # 7. Add in PK0170 label to op 1 (non-kit issue)

    PK0170_row = build_bomstructure_row(
        parent_part=stock_code,
        component="PK0170",
        overlays={
            "QtyPer": "1",
            "QtyPerEnt": "1",
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

    DPPICK_row = build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": 0,
            "Operation": next_op,
            "WorkCentre": "DPPICK"
        }
    )

    DPCHK_row = build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": 0,
            "Operation": next_op + 1,
            "WorkCentre": "DPCHK"
        },
        overlays={
            "Milestone": "N"
        }
    )

    DPPACK_row = build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": 0,
            "Operation": next_op + 2,
            "WorkCentre": "DPPACK"
        },     
    )

    DPDESP_row = build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": 0,
            "Operation": next_op + 3,
            "WorkCentre": "DPDESP"
        }   
    )

    for row in [DPPICK_row, DPCHK_row, DPPACK_row, DPDESP_row]:
        append_single_record(
            table="BomOperations",
            row=row
        )


    # 9. Copy this whole BOM/op structure to route 5 (supplant previous route)

    delete_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": "5"
        }
    )

    delete_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code,
            "Route": "5"
        }
    )

    copy_bomops_to_new_route(
        source_stock_code=stock_code,
        source_route=0,
        dest_stock_code=stock_code,
        dest_route=5
    )


    # 10. Copy this whole BOM/op structure to route 6 (supplant previous route)

    delete_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": "6"
        }
    )

    delete_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code,
            "Route": "6"
        }
    )

    copy_bomops_to_new_route(
        source_stock_code=stock_code,
        source_route="0",
        dest_stock_code=stock_code,
        dest_route="6"
    )


    # 11. In route 6, add "DPDRL" between DPCHK and DPPACK (op 7)

    op_after_wms = get_next_op_number(stock_code=stock_code,route=6)

    update_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": "6",
            "WorkCentre": "DPDESP"
        },
        update_data={
            "Operation": op_after_wms
        }
    )

    update_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": "6",
            "WorkCentre": "DPPACK"
        },
        update_data={
            "Operation": op_after_wms - 1
        }
    )

    DPDRL_row = build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": 6,
            "Operation": op_after_wms - 2,
            "WorkCentre": "DPDRL"
        } 
    )

    append_single_record(
        table="BomOperations",
        row=DPDRL_row
    )

    # 12. Change zInvExtra LinkedStockCode to point at the parent SKU itself

    update_records(
        table="zInvExtra",
        criteria={
            "StockCode": stock_code
        },
        update_data={
            "LinkedStockCode": stock_code
        }
    )

    # 13. Change Parent SKU Long Description to "MTO"

    update_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        update_data={
            "LongDesc": "MTO"
        }
    )


def jpull_range_to_mto():

    door_range = ["PJMRG1245X296","PJMRG1245X396","PJMRG1245X496","PJMRG1245X596","PJMRG140X296","PJMRG140X396","PJMRG140X446","PJMRG140X496","PJMRG140X596","PJMRG140X796","PJMRG140X896","PJMRG140X996","PJMRG175X396","PJMRG175X496","PJMRG175X596","PJMRG283X496","PJMRG283X596","PJMRG283X796","PJMRG283X896","PJMRG283X996","PJMRG355X496","PJMRG355X596","PJMRG355X796","PJMRG355X896","PJMRG355X996","PJMRG450X396","PJMRG450X596","PJMRG490X596","PJMRG570X296","PJMRG570X396","PJMRG570X446","PJMRG570X496","PJMRG570X596","PJMRG645X596","PJMRG715X146","PJMRG715X236","PJMRG715X296","PJMRG715X346","PJMRG715X396","PJMRG715X446","PJMRG715X496","PJMRG715X596","PJMRG895X236","PJMRG895X296","PJMRG895X396","PJMRG895X496","PJMRG895X596","PJMRG980X596","PJMRGSQ110X596"]

    for sku in door_range:
        switch_jpull_stocked_to_mto(sku)