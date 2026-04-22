from tools.sql import get_multiple_records, get_single_record
from validation.general_validation import check_if_in_table

'''
1. Park current route 0 BOM in alternate route "A"
2. Copy BOM from subcomponent/linked item
3. Replace first op with DSAWC
4. Remove DSHRIN op
5. Remove PK9* layflat material
6. Re-assign B0167/* packing piece to DJSHAP op (op 4)
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
        table="InvMaster"
    )

    if not sku_exists:
        print("SKU not found in InvMaster, terminating.")

    # Check if route A is free for the stock code, if not, prompt user to check, and ask if you want to overwrite, swap, or terminate
    route_a_ops_exists = check_if_in_table(
        stock_code=stock_code,
        table="BomOperations",
        route="A"
    )

    route_a_bom_exists = check_if_in_table(
        stock_code=stock_code,
        table="BomStructure",
        route="A"
    )

    if route_a_ops_exists or route_a_bom_exists:
        print("Records present in Route A structure & routing" \
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
