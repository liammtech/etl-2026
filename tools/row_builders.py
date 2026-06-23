from dataclasses import fields, is_dataclass
from config.loaders.defaults import load_row_defaults
from domain.wip.materials import apply_wip_material_uom
from models.tables import MODEL_REGISTRY
from typing import Any, Type
import yaml

# Table row creators - which utilise a generic _build_row()

# Whilst these interfaces currently present as a duplicated function, there may be validation/transformation steps
# to build in later, specific to each table

# Hence, the decision was to keep the interfaces separated, as opposed to having a generic, catch-all row builder


# -- GENERAL --

def load_wip_material_uom_flags() -> dict[str, dict[str, str]]:
    with open("config/uom/wip_material_uom_flags.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data["wip_material_uom_flags"]


def _build_row(
    *,
    table_name: str,
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:

    table_name = table_name.replace("[", "").replace("]", "")

    model = MODEL_REGISTRY[table_name]

    if not is_dataclass(model):
        raise TypeError(f"{model} is not a dataclass")

    row = load_row_defaults(table_name=table_name)

    model_fields = {field.name for field in fields(model)}

    unknown_values = set(values) - model_fields
    if unknown_values:
        raise ValueError(
            f"Unknown fields for {model.__name__}: {unknown_values}"
        )

    missing_required = {
        field.name
        for field in fields(model)
        if field.default is field.default_factory
        and field.name not in values
        and field.name not in row
    }

    if missing_required:
        raise ValueError(
            f"Missing required fields for {model.__name__}: {missing_required}"
        )

    row.update(values)

    if overlays:
        row.update(overlays)

    return row


# -- STOCK CODES --

def build_invmaster_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="InvMaster",
        values=values,
        overlays=overlays,
    )


def build_invmasterplus_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="[InvMaster+]",
        values=values,
        overlays=overlays,
    )


def build_zinvextra_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="zInvExtra",
        values=values,
        overlays=overlays,
    )


def build_invwarehouse_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="InvWarehouse",
        values=values,
        overlays=overlays,
    )


def build_invwarehouseplus_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="[InvWarehouse+]",
        values=values,
        overlays=overlays,
    )


def build_arcuststkxref_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="ArCustStkXref",
        values=values,
        overlays=overlays,
    )


def build_invnarration_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="InvNarration",
        values=values,
        overlays=overlays,
    )


def build_invnarrationhdr_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="InvNarrationHdr",
        values=values,
        overlays=overlays,
    )


def build_admmultimedia_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="AdmMultimedia",
        values=values,
        overlays=overlays,
    )


# -- BOMs --

def build_bomstructure_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="BomStructure",
        values=values,
        overlays=overlays,
    )


def build_bomoperations_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="BomOperations",
        values=values,
        overlays=overlays,
    )


def build_bomstructureplus_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="[BomStructure+]",
        values=values,
        overlays=overlays,
    )


def build_bomoperationsplus_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="[BomOperations+]",
        values=values,
        overlays=overlays,
    )


# -- Pricing -- 

def build_invprice_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="InvPrice",
        values=values,
        overlays=overlays,
    )

def build_sorcontractprice_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
        table_name="SorContractPrice",
        values=values,
        overlays=overlays,
    )

# -- WIP --

def build_wipjoballlab_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_row(
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

    return _build_row(
        table_name="WipJobAllMat",
        values=values,
        overlays=overlays
    )
