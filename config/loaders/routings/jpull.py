from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


JPULL_OPS_PATH = Path("config/data/routings/jayl_routings.yml")


from typing import Literal


def get_jpull_template_name(
    *,
    edge_type: Literal["wrapped", "edged"],
    drilled: bool,
    destination: Literal["stocked", "mto", "oem"],
) -> str:
    """
    Resolve frontend J-Pull routing options to a routing template name.

    Args:
        edge_type:
            wrapped
            edged

        drilled:
            Whether drilling operations should be included.

        destination:
            stocked
            mto
            oem

    Returns:
        Template name from the J-Pull routing configuration.
    """

    template_prefixes = {
        ("stocked", False): "stocked",
        ("stocked", True): "stocked_predrilled",
        ("mto", False): "mto",
        ("mto", True): "mto_drilled",
        ("oem", False): "oem",
        ("oem", True): "oem_drilled",
    }

    try:
        prefix = template_prefixes[(destination, drilled)]
    except KeyError:
        raise ValueError(
            f"Unsupported destination/drilled combination: "
            f"{destination!r}, {drilled!r}"
        ) from None

    return f"{prefix}_{edge_type}"


@lru_cache
def load_jpull_operations_config() -> dict[str, Any]:
    with JPULL_OPS_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("J-Pull operations config must be a mapping.")

    if "fragments" not in data:
        raise ValueError("J-Pull operations config missing 'fragments'.")

    if "templates" not in data:
        raise ValueError("J-Pull operations config missing 'templates'.")

    return data


from typing import Any


def resolve_jpull_operations_template(
    template_name: str,
) -> list[dict[str, Any]]:
    config = load_jpull_operations_config()

    fragments = config["fragments"]
    templates = config["templates"]

    if template_name not in templates:
        raise ValueError(
            f"Unknown J-Pull template {template_name!r}. "
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
            fragment_ops = fragments[fragment_group][fragment_name]
        except KeyError:
            raise ValueError(
                f"Template {template_name!r} references unknown fragment "
                f"{fragment_group}.{fragment_name!r}."
            ) from None

        resolved_ops.extend(fragment_ops)

    return [
        {
            "operation": index,
            "work_centre": op["work_centre"],
            "milestone": op["milestone"],
        }
        for index, op in enumerate(resolved_ops, start=1)
    ]