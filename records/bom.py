from typing import Any
from records.builder import build_row

# -- BOMs --

def build_bomstructure_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="BomStructure",
        values=values,
        overlays=overlays,
    )


def build_bomoperations_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="BomOperations",
        values=values,
        overlays=overlays,
    )


def build_bomstructureplus_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="[BomStructure+]",
        values=values,
        overlays=overlays,
    )


def build_bomoperationsplus_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="[BomOperations+]",
        values=values,
        overlays=overlays,
    )
