from pprint import pprint
import tools.sql as sql
from validation.kk_validation import check_if_d_code, check_if_non_d_code_exists

'''
REMOVE D CODES

1. Accept D code as argument 
2. Check that it is in fact a "D" code
    - If not, warn and terminate
3. Check that it's non-D equivalent exists
    - If not, warn and terminate
4. Retrieve a list (List A) of all BOM instances, including:
    - ParentPart
    - parent part's ProductClass
    - Route
    - SequenceNum
    - Component
5. Filter out any entries from this list where the product class of the Parent Part does not begin with "KK"
6. Identify any entries from this list where the product configuration has the part as undrilled 
    - add them to new list (List B)
    - include same fields as List A
    - compare them against a config list
    - these D codes will still be swapped, but will be missed out when adding in the drilling ops
    - e.g. a 715x446 door will be drilled when part of the 450 unit (FKxxxx39), but not when sold as an appliance door (FKxxxx45)
7. For every entry in List A, swap the D-code door for the non-D code (keying in by ParentPart and Route)
8. From List A, filter out all records that have a match in List B (call this List C)
9. For all entries in List C:
    - Check whether the routing has a DPDRL operation
    - If not, insert it after DPCHK
    - This inserts a drilling op only on those codes that need it
'''

# 1. Accept D code as argument 

def sub_out_d_code(stock_code: str) -> None: 

    # 2. Check that it is in fact a "D" code
    if not check_if_d_code(stock_code=stock_code):
        print(f"\n\nStock code {stock_code} is not a 'D' code - terminating.\n\n")
        return

    # 3. Check that it's non-D equivalent exists
    if not check_if_non_d_code_exists(stock_code=stock_code):
        print(f"\n\nNon-'D'-code equivalent for {stock_code} doesn't exist, setup is required - terminating.\n\n")
        return
    
    # 4. Retrieve a list (List A) of all BOM instances, including:
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

    # 5. Filter out any entries from this list where the product class of the Parent Part does not begin with "KK"

    d_code_bom_instances = []

    for row in d_code_bom_query_result:
        if row.ProductClass[0:2] == "KK":
            d_code_bom_instances.append(row)

    pprint(d_code_bom_instances)

    # 6. Identify any entries from this list where the product configuration has the part as undrilled 