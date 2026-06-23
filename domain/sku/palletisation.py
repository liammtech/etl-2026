import db.sql as sql
from config.loaders.materials import get_pallets
from typing import Literal
from pprint import pprint

# Func: Decide whether need profile or door pallet
# Func: Decide pallet size
# Func: decide pallet qty/layers/stack
# Func: update InvMaster and zInvExtra values

# Func: Bring em altogether (including a pallet BOM posting)

# 1. Door or profile pallet?
# Largely works from product class, but there some instances where the size of a non-wrapped SKU
# e.g. a plinth would want to be on a profile pallet - namely length


def _determine_sku_type(
    stock_code: str
) -> Literal["door", "profile", "component", "invalid"]:
    sku_type = sql.get_single_record(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        },
        return_columns=["ProductClass"],
        flatten=True
    )

    match sku_type:
        case "CJAY":
            return "door"
        case "DR5P":
            return "door"
        case "LLDR":
            return "door"
        case "MEMP":
            return "door"
        case "PJAY":
            return "door"
        case "PRWS":
            return "profile"
        case "COMP":
            return "component"
        case _:
            return "invalid"
    
def determine_door_pallet(
    stock_code: str
) -> str:
    pass


def determine_pallet_spec(
    stock_code: str
) -> str:
    
    product_class, height, width = sql.get_single_record(
        table="InvMaster AS i",
        joins=[
            sql.Join(
                table="zInvExtra AS z",
                on="i.StockCode = z.StockCode"
            )
        ],
        criteria={
            "i.StockCode": stock_code
        },
        return_columns=[
            "i.ProductClass",
            "z.Height",
            "z.Width"
        ]
    )

    pallets = get_pallets()

    # pprint(pallets['PKDR-A']['length'])

