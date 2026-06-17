from pprint import pprint
import tools.sql as sql
from validation.kk_validation import check_if_d_code, check_if_non_d_code_exists, check_if_valid_kk_door_sales_code, check_if_valid_main_range_KK_code

'''
REMOVE D CODES

1. Accept D code as argument 
2. Check that it is in fact a "D" code
    - If not, warn and terminate
3. Check that it's non-D equivalent exists
    - If not, warn and terminate
4. Retrieve a list of all BOM instances, including:
    - ParentPart
    - parent part's ProductClass
    - Route
    - SequenceNum
    - Component
5. Validate each parent code in the list, they fall into three categories:
    - Kitchen Kit main range: make a list to treat these one way
    - Kitchen Kit doors: make a list to treat these another way
    - Anything else: an oddity, make a list to print to the terminal when the job is done, because they probably shouldn't be working from D codes
6. Main range code treatment - for each row:
    - See function notes
7. Door sale code treatment
    - See function notes
8. Anomalies treatment
'''

# 1. Accept D code as argument 
def sub_out_d_code(stock_code: str) -> None:
    '''

    '''

    # 2. Check that it is in fact a "D" code
    if not check_if_d_code(stock_code=stock_code):
        print(f"\n\nStock code {stock_code} is not a 'D' code - terminating.\n\n")
        return

    # 3. Check that it's non-D equivalent exists
    if not check_if_non_d_code_exists(stock_code=stock_code):
        print(f"\n\nNon-'D'-code equivalent for {stock_code} doesn't exist, setup is required - terminating.\n\n")
        return
    
    # 4. Retrieve a list of all BOM instances, including:
    d_code_bom_query_result = sql.get_multiple_records(
        table="InvMaster AS i",
        joins=[
            sql.Join(                       # When used in another module, Join class is available via sql module
                table="BomStructure AS b",
                on="i.StockCode = b.ParentPart",
                join_type="INNER"
            )
        ],
        criteria={
            "b.Component": stock_code
        },
        return_columns=[
            "b.ParentPart",
            "i.ProductClass",
            "b.Route",
            "b.SequenceNum",
            "b.Component"
        ]
    )

    # 5. Validate each parent code in the list

    main_range_codes = []
    door_sales_codes = []
    anomalies = []

    for row in d_code_bom_query_result:
        if check_if_valid_main_range_KK_code(row.ParentPart):
            main_range_codes.append(row)
        elif check_if_valid_kk_door_sales_code(row.ParentPart):
            door_sales_codes.append(row)
        else:
            anomalies.append(row)

    pprint(f"Main range codes: \n{main_range_codes}\n\n")
    pprint(f"Door sales codes: \n{door_sales_codes}\n\n")
    pprint(f"Anomalies: \n{anomalies}\n\n")

    # 6. Main range code treatment - for each row:

    # OPS
    # - Check if the product config is supposed to have any drilling at all
    # - Check if all Kitchen Kit standard routes have a DPDRL operation
    # - If any don't, insert DPDRL into the operations list for that route

    # BOMS
    # - Swap out the D code for it's non-D variant, for each route
    # - Check if this item is supposed to be drilled
    # - If yes, for each route, check that drilling instruction is in place:
    #   - Get SequenceNum (already have ParentPart, Route, Component)
    #   - Using all four keys, check if there is an associated BomStructure+ record
    #   - If there is no record, create one
    #   - If there is a record, check whether the drilling instruction is correct via config
    #   - If incorrect, correct it
    #   - Continue to next row