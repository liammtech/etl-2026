from functools import reduce
from tools.sql import update_records, get_single_record, get_multiple_records
from tools.validation import check_if_in_table, RecordNotFoundError
import tools.calculations.pressed_qty_per_calcs as pressed

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
    
    # TODO: various validation steps e.g. is it MEMP product class, is the BOM as expected

    ## GET DOOR DIMS
    door_dims = get_single_record(
        table="zInvExtra",
        criteria={
            "StockCode": stock_code
        },
        return_columns=[
            "Height",
            "Width",
            "Thickness"
        ]
    )

    door_height = int(door_dims.Height)
    door_width = int(door_dims.Width)
    door_thickness = int(door_dims.Thickness)

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

    mel_code = [item for sublist in mel_code_list for item in sublist][0]
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

    pv_code = [item for sublist in pv_code_list for item in sublist][0]

    # Get pallet code
    pallet_code_list = get_multiple_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code,
            "Component": "PKDR%"
        },
        return_columns=["Component"]
    )

    pallet_code = [item for sublist in pallet_code_list for item in sublist][0]


    # Get board height and width
    mel_code_dims = get_single_record(
        table="zInvExtra",
        criteria={
            "StockCode": mel_code
        },
        return_columns=[
            "Height",
            "Width"
        ]
    )

    mel_code_height = int(mel_code_dims.Height)
    mel_code_width = int(mel_code_dims.Width)

    print(f"Board height is {mel_code_height}, width is {mel_code_width}")

    # Get foil width
    foil_width_mtrs = get_single_record(
        table="InvMaster",
        criteria={
            "StockCode": pv_code
        },
        return_columns=["ConvFactAltUom"]
    )

    foil_width_mm = int(foil_width_mtrs[0] * 1000)

    # Get max pallet quantity
    pallet_max_qty_result = get_single_record(
        table="zInvExtra",
        criteria={
            "StockCode": stock_code
        },
        return_columns=[
            "PalletPackSize"
        ]
    )
    pallet_max_qty = int(pallet_max_qty_result.PalletPackSize)

    ## CALCULATE QUANTITIES

    mel_qty_per = pressed.calculate_mel_board_qty(
        door_height=door_height,
        door_width=door_width,
        board_height=mel_code_height,
        board_width=mel_code_width
    )

    gl100_qty_per = pressed.calculate_glue_qty(
        door_height=door_height,
        door_width=door_width,
        door_depth=door_thickness
    )

    gl101_qty_per = pressed.calculate_glue_hardener_qty(
        door_height=door_height,
        door_width=door_width,
        door_depth=door_thickness
    )

    foil_qty_per = pressed.calculate_foil_qty(
        foil_width=foil_width_mm,
        door_height=door_height,
        door_width=door_width,
        door_depth=door_thickness
    )

    pallet_qty_per = pressed.calculate_pallet_qty(
        pallet_max_qty=pallet_max_qty
    )

    material_qty_pers = {
        mel_code: mel_qty_per,
        "GL100": gl100_qty_per,
        "GL101": gl101_qty_per,
        pv_code: foil_qty_per,
        pallet_code: pallet_qty_per
    }

    for i, j in material_qty_pers.items():
        print(f"{i}: {j}")

    ## SET QUANTITIES

    for component in material_qty_pers:
        update_records(
            table="BomStructure",
            criteria={
                "ParentPart": stock_code,
                "Component": component
            },
            update_data={
                "QtyPer": material_qty_pers[component],
                "QtyPerEnt": material_qty_pers[component]
            }
        )