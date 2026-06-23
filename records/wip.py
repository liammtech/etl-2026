from typing import Any
from records.builder import build_row
from domain.wip.materials import apply_wip_material_uom

# -- WIP --

def build_wipjoballlab_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="WipJobAllLab",
        values=values,
        overlays=overlays,
    )


def build_wipjoballmat_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:

    values = apply_wip_material_uom(values)

    values.pop("QtyPer", None)

    print(values)

    return build_row(
        table_name="WipJobAllMat",
        values=values,
        overlays=overlays
    )
