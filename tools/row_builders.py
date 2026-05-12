from dataclasses import fields, is_dataclass
from tools.config_tools.config_loader import load_row_defaults
from models import MODEL_REGISTRY
from typing import Any, Type


def build_row(
    *,
    table_name: str,
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:

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


def build_wipjoballmat_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="WipJobAllMat",
        values=values,
        overlays=overlays,
    )


def build_wipjoballlab_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="WipJobAllLab",
        values=values,
        overlays=overlays,
    )