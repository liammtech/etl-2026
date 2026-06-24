from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml


EDGED_DOORS_ROUTINGS_PATH = Path(
    "config/data/routings/lldr_routings.yml"
)


def get_edged_door_template_name(
    *,
    source_method: Literal["nest", "rout"],
    destination: Literal["stocked", "mto", "oem"],
    drilled: bool,
) -> str:
    template_map = {
    ("nest", "stocked", False): "edged_stocked_nested",
    ("nest", "stocked", True): "edged_stocked_nested_drilled",

    ("rout", "stocked", False): "edged_stocked_routed",
    ("rout", "stocked", True): "edged_stocked_routed_drilled",

    ("nest", "mto", False): "edged_mto_nested",
    ("nest", "mto", True): "edged_mto_nested_drilled",

    ("rout", "mto", False): "edged_mto_routed",
    ("rout", "mto", True): "edged_mto_routed_drilled",

    ("nest", "oem", False): "edged_oem_nested",
    ("nest", "oem", True): "edged_oem_nested_drilled",

    ("rout", "oem", False): "edged_oem_routed",
    ("rout", "oem", True): "edged_oem_routed_drilled",
    }

    try:
        return template_map[(source_method, destination, drilled)]
    except KeyError:
        raise ValueError(
            f"Unsupported edged door routing combination: "
            f"{source_method=}, {destination=}, {drilled=}"
        ) from None


@lru_cache
def load_edged_door_routings_config() -> dict[str, Any]:
    with EDGED_DOORS_ROUTINGS_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Edged door routings config must be a mapping.")

    if "fragments" not in data:
        raise ValueError("Edged door routings config missing 'fragments'.")

    if "templates" not in data:
        raise ValueError("Edged door routings config missing 'templates'.")

    return data


def _get_fragment_operations(
    *,
    fragment: dict[str, Any],
    context: dict[str, str],
) -> list[dict[str, Any]]:
    if "operations" in fragment:
        operations = fragment["operations"]

        if not isinstance(operations, list):
            raise ValueError("'operations' must be a list.")

        return operations

    if "variants" in fragment:
        variants = fragment["variants"]

        if not isinstance(variants, dict):
            raise ValueError("'variants' must be a mapping.")

        if len(variants) != 1:
            raise ValueError(
                "Only one variant selector per fragment is currently supported."
            )

        variant_key, variant_options = next(iter(variants.items()))

        if variant_key not in context:
            raise ValueError(
                f"Fragment requires context value {variant_key!r}."
            )

        selected_value = context[variant_key]

        if selected_value not in variant_options:
            raise ValueError(
                f"Unsupported {variant_key!r} value {selected_value!r}. "
                f"Valid values are: {sorted(variant_options)}"
            )

        selected_fragment = variant_options[selected_value]

        return _get_fragment_operations(
            fragment=selected_fragment,
            context=context,
        )

    raise ValueError(
        "Fragment must contain either 'operations' or 'variants'."
    )


def resolve_edged_door_operations_template(
    *,
    template_name: str,
    context: dict[str, str],
) -> list[dict[str, Any]]:
    config = load_edged_door_routings_config()

    fragments = config["fragments"]
    templates = config["templates"]

    if template_name not in templates:
        raise ValueError(
            f"Unknown edged door template {template_name!r}. "
            f"Valid templates are: {sorted(templates)}"
        )

    template = templates[template_name]
    steps = template.get("steps")

    if not isinstance(steps, list):
        raise ValueError(
            f"Template {template_name!r} must contain a 'steps' list."
        )

    resolved_ops: list[dict[str, Any]] = []

    for step in steps:
        if not isinstance(step, dict) or len(step) != 1:
            raise ValueError(
                f"Invalid step in template {template_name!r}: {step!r}"
            )

        fragment_group, fragment_name = next(iter(step.items()))

        try:
            fragment = fragments[fragment_group][fragment_name]
        except KeyError:
            raise ValueError(
                f"Template {template_name!r} references unknown fragment "
                f"{fragment_group}.{fragment_name!r}."
            ) from None

        resolved_ops.extend(
            _get_fragment_operations(
                fragment=fragment,
                context=context,
            )
        )

    return [
        {
            "operation": index,
            "work_centre": op["work_centre"],
            "milestone": op["milestone"],
        }
        for index, op in enumerate(resolved_ops, start=1)
    ]