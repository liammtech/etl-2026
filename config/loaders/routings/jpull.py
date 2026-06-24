from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml


JPULL_OPS_PATH = Path("config/data/routings/jayl_routings.yml")


def get_jpull_template_name(
    *,
    edge_type: Literal["wrapped", "edged"],
    drilled: bool,
    destination: Literal["stocked", "mto", "oem"],
) -> str:
    config = load_jpull_operations_config()

    templates = config["templates"]

    matches = []

    for template_name, template in templates.items():

        selector = template.get("selector", {})

        if selector == {
            "edge_type": edge_type,
            "destination": destination,
            "drilled": drilled,
        }:
            matches.append(template_name)

    if not matches:
        raise ValueError(
            f"No J-Pull routing template found for "
            f"{edge_type=}, {destination=}, {drilled=}"
        )

    if len(matches) > 1:
        raise ValueError(
            f"Multiple J-Pull routing templates found for "
            f"{edge_type=}, {destination=}, {drilled=}: {matches}"
        )

    return matches[0]


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