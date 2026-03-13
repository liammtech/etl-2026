from functools import reduce
from tools.sql import update_records, get_single_record, get_multiple_records
from tools.validation import check_if_in_table, RecordNotFoundError

# Membrane Pressed - Standard
def memp_std_single(stock_code: str):
    bom_records_exist = check_if_in_table(
        stock_code=stock_code,
        table="BomStructure",
        sql_getter_func=get_multiple_records
    )

    if not bom_records_exist:
        raise RecordNotFoundError(f"No record found for {stock_code} in table BomStructure")

    zInvExtra_exists = check_if_in_table(
        stock_code=stock_code,
        table="zInvExtra",
        sql_getter_func=get_single_record
    )

    if not zInvExtra_exists:
        raise RecordNotFoundError(f"No record found for {stock_code} in table zInvExtra")
    
    # TODO: validate the BOM records themselves

    ## GET MATERIAL CODES

    # Get board MEL code
    mel_code_list = get_multiple_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code,
            "Component": "MEL%"
        },
        return_columns=["Component"]
    )

    mel_code = [item for sublist in mel_code_list for item in sublist]
    print(f"Foil code for {stock_code} is {mel_code}")

    # Get foil PV code
    pv_code_list = get_multiple_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code,
            "Component": "PV%"
        },
        return_columns=["Component"]
    )

    pv_code = [item for sublist in pv_code_list for item in sublist]
    print(f"Foil code for {stock_code} is {pv_code}")

    # Get foil width