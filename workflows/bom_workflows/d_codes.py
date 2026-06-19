from pprint import pprint
import db.sql as sql
from tools.bom_tools.bom_organisation import check_if_work_centre_in_routing, insert_operation, defrag_routing
import validation.kk_validation as kk
# check_if_d_code, check_if_non_d_code_exists, check_if_valid_kk_door_sales_code, check_if_valid_main_range_KK_code, check_if_cab_config_has_any_drilled_doors, check_if_door_config_is_drilled, check_if_standalone_door_is_drilled

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
    if not kk.check_if_d_code(stock_code=stock_code):
        print(f"\n\nStock code {stock_code} is not a 'D' code - terminating.\n\n")
        return

    # 3. Check that it's non-D equivalent exists
    if not kk.check_if_non_d_code_exists(stock_code=stock_code):
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
        if kk.check_if_valid_main_range_KK_code(row.ParentPart):
            main_range_codes.append(row)
        elif kk.check_if_valid_kk_door_sales_code(row.ParentPart):
            door_sales_codes.append(row)
        else:
            anomalies.append(row)

    pprint(f"Main range codes: \n{main_range_codes}\n\n")
    pprint(f"Door sales codes: \n{door_sales_codes}\n\n")
    pprint(f"Anomalies: \n{anomalies}\n\n")

    # 6. Main range code treatment - for each row:
    for row in main_range_codes:

        # OPS
        # - Check if the product config is supposed to have any drilling at all
        drilling_reqd = kk.check_if_cab_config_has_any_drilled_doors(stock_code=row.ParentPart)
        
        # Note: Do not get caught up in trying to fix missing routes - that is for a different function. Focus on the ones in the list

        # If drilling is required:
        if drilling_reqd:

            # - Check if the operations list for that route is missing DPDRL
            dpdrl_exists = check_if_work_centre_in_routing(
                stock_code=row.ParentPart,
                route=row.Route,
                work_centre="DPDRL"
            )

            # - If it is missing, insert DPDRL into the operations list for that route
            if not dpdrl_exists:
                insert_operation(
                    stock_code=row.ParentPart,
                    route=row.Route,
                    work_centre="DPDRL",
                    after_work_centre="DPCHK"
                )



        # BOMS
        # - Swap out the D code for it's non-D variant, for each route
        new_component = row.Component[:-1]

        print(new_component)

        sql.update_records(
            table="BomStructure",
            criteria={
                "ParentPart": row.ParentPart,
                "Route": row.Route,
                "Component": row.Component
            },
            update_data={
                "Component": new_component
            }
        )

        defrag_routing(stock_code=row.ParentPart, route=row.Route)

        #  TODO: Validate drilling - should be it's own function/workflow also
        # - Check if this item is supposed to be drilled
        # - If yes, for each route, check that drilling instruction is in place:
        #   - Get SequenceNum (already have ParentPart, Route, Component)
        #   - Using all four keys, check if there is an associated BomStructure+ record
        #   - If there is no record, create one
        #   - If there is a record, check whether the drilling instruction is correct via config
        #   - If incorrect, correct it
        # - Continue to next row

    # 7. Door range code treatment - for each row:
    for row in door_sales_codes:

        # OPS
        # - Check if the standalone door is supposed to have drilling
        drilling_reqd = kk.check_if_standalone_door_is_drilled(door_sales_code=row.ParentPart)

        print(f"Standalone door {row.Component} drilling required: {drilling_reqd}")
        # - Check if all Kitchen Kit standard routes for the parent part have a DPDRL operation
        if drilling_reqd:

            dpdrl_exists = check_if_work_centre_in_routing(
                stock_code=row.ParentPart,
                route=row.Route,
                work_centre="DPDRL"
            )

        # - If any don't, insert DPDRL into the operations list for that route

            if not dpdrl_exists:
                insert_operation(
                    stock_code=row.ParentPart,
                    route=row.Route,
                    work_centre="DPDRL",
                    after_work_centre="DPCHK"
                )

        # BOMS
        # - Swap out the D code for it's non-D variant, for each route

        new_component = row.Component[:-1]

        print(new_component)

        sql.update_records(
            table="BomStructure",
            criteria={
                "ParentPart": row.ParentPart,
                "Route": row.Route,
                "Component": row.Component
            },
            update_data={
                "Component": new_component
            }
        )

        defrag_routing(stock_code=row.ParentPart, route=row.Route)

        #  TODO: Validate drilling - should be it's own function/workflow also
        # - Check if this item is supposed to be drilled
        # - If yes, for each route, check that drilling instruction is in place:
        #   - Get SequenceNum (already have ParentPart, Route, Component)
        #   - Using all four keys, check if there is an associated BomStructure+ record
        #   - If there is no record, create one
        #   - If there is a record, check whether the drilling instruction is correct via config
        #   - If incorrect, correct it
        # - Continue to next row

    #  *** The only difference between steps 6 and 7 is how the validation is done
    #  *** Main range is against main range config, door range is against door range config

    #  8. Anomalies treatment - for each row:

    if anomalies:
        print("The following rows are non-standard setups, please check")
        for row in anomalies:
            print(f"\n{row}")

        # Add to a list for a warning print statement, 
        # Explain that these need to be dealt with in isolation
        # This is because they're a non-standard setup and likely an error

    # TERMINATE