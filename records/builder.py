from dataclasses import fields, is_dataclass
from config.loaders.defaults import load_row_defaults
from domain.wip.materials import apply_wip_material_uom
from models.tables import MODEL_REGISTRY
from typing import Any


def build_row(
    *,
    table_name: str,
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> Any:
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

    row.update(values)

    if overlays:
        row.update(overlays)

    return model(**row)