from typing import Any
import yaml
from functools import lru_cache
from decimal import Decimal


@lru_cache
def load_wip_material_uom_flags() -> dict[str, dict[str, str]]:
    with open("config/uom/wip_material_uom_flags.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data["wip_material_uom_flags"]


def apply_wip_material_uom(values: dict[str, Any]) -> dict[str, Any]:
    values = values.copy()

    stock_code = values["StockCode"]
    uom_flag = values.get("UomFlag", "S")

    uom_config = load_wip_material_uom_flags()

    if uom_flag not in uom_config:
        raise ValueError(
            f"Unsupported UomFlag {uom_flag!r} for stock code {stock_code!r}"
        )

    source_qty_field = uom_config[uom_flag]["source_qty_field"]

    if source_qty_field not in values:
        raise ValueError(
            f"UomFlag {uom_flag!r} expects {source_qty_field!r}, "
            f"but it was not supplied for {stock_code!r}"
        )

    entered_qty = Decimal(values[source_qty_field])

    stocking_qty = convert_to_stocking_qty(
        entered_qty=entered_qty,
        values=values,
        uom_flag=uom_flag,
    )

    values["UnitQtyReqdEnt"] = entered_qty
    values["NetUnitQtyReqdEnt"] = entered_qty

    values["UnitQtyReqd"] = stocking_qty
    values["NetUnitQtyReqd"] = stocking_qty

    values["Uom"] = uom_flag

    return values


def convert_to_stocking_qty(
    *,
    entered_qty: Decimal,
    values: dict[str, Any],
    uom_flag: str,
) -> Decimal:
    if uom_flag == "S":
        return entered_qty

    conv_fact = Decimal(values["ConvFactUom"])
    conv_mul_div = values["ConvMulDiv"]

    if conv_mul_div == "M":
        return entered_qty * conv_fact

    if conv_mul_div == "D":
        return entered_qty / conv_fact

    raise ValueError(
        f"Unsupported ConvMulDiv {conv_mul_div!r} "
        f"for stock code {values['StockCode']!r}"
    )

def get_uom_conversion_fields(
    *,
    invmaster_row: Any,
    uom_flag: str,
) -> dict[str, Any]:
    match uom_flag:
        case "S":
            return {
                "ConvFactUom": 1,
                "ConvMulDiv": "M",
            }

        case "A":
            return {
                "ConvFactUom": invmaster_row.ConvFactAltUom,
                "ConvMulDiv": invmaster_row.ConvMulDiv,
            }

        case "O":
            return {
                "ConvFactUom": invmaster_row.ConvFactOthUom,
                "ConvMulDiv": invmaster_row.MulDiv,
            }

        case "M":
            return {
                "ConvFactUom": invmaster_row.ConvFactMuM,
                "ConvMulDiv": "M",
            }

        case _:
            raise ValueError(f"Unsupported UoM flag: {uom_flag!r}")