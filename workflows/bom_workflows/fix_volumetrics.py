import tools.sql as sql
from fnmatch import fnmatch

def fix_door_volumetrics(stock_code: str) -> None:

    door_dims = sql.get_single_record(
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

    door_height, door_width, door_thickness = [door_dims.Height, door_dims.Width, door_dims.Thickness]

    door_materials = sql.get_multiple_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code,
            "Route": "0"
        },
        return_columns=[
            "Component"
        ]
    )

    mfc_flag = False

    unpacked_mats = [item for sublist in door_materials for item in sublist]

    if any(fnmatch(item, "MFC*") for item in unpacked_mats):
        mfc_flag = True

    kg_multiplier = 750

    if mfc_flag:
        kg_multiplier = 650

    door_m2 = (door_height / 1000) * (door_width / 1000)
    door_m3 = door_m2 * (door_thickness / 1000)
    door_kg = door_m3 * kg_multiplier

    door_m2 = round(door_m2, 6)
    door_m3 = round(door_m3, 6)
    door_kg = round(door_kg, 6)

    sql.update_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        update_data={
            "ConvFactAltUom": door_m2,
            "ConvFactOthUom": door_m3,
            "Mass": door_kg
        }
    )

def fix_door_volumetrics_range(stock_code: str):    

    door_range_result = sql.get_multiple_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code,
        },
        return_columns=[
            "StockCode"
        ]
    )
    
    # door_range = [item for sublist in door_range_result for item in sublist]
    door_range = ["FFPDLO006","FFPDLO007","FFPDLO008","FFPDLO009","FFPDLO010","FFPDLO011","FFPDMW006","FFPDMW007","FFPDMW008","FFPDMW009","FFPDMW010","FFPDMW011","FFPDUO006","FFPDUO007","FFPDUO008","FFPDUO009","FFPDUO010","FFPDUO011","FFPRMC006","FFPRMC007","FFPRMC008","FFPRMC009","FFPRMC010","FFPRMC011","FFPRLO006","FFPRLO007","FFPRLO008","FFPRLO009","FFPRLO010","FFPRLO011","FFPRUO006","FFPRUO007","FFPRUO008","FFPRUO009","FFPRUO010","FFPRUO011"]

    for sku in door_range:
        fix_door_volumetrics(sku)