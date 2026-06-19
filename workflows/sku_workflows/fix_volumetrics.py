import db.sql as sql
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
    door_range = ["PFMW127","PFMCB127","PFMCM127","PFMDG127","PFMG127","PFMSG127","ORAGC127","ORAGG127","ORAGW127","ORAMA127","ORAMZ127","ORAMQ127","ORAMC127","ORAMG127","ORAMW127"]

    for sku in door_range:
        fix_door_volumetrics(sku)