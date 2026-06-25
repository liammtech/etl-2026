from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml


EDGED_DOORS_ROUTINGS_PATH = Path(
    "config/data/routings/edged_routings.yml"
)


SourceMethod = Literal["nest", "rout"]
Destination = Literal["stocked", "mto", "oem"]
ProductionDrillWorkCentre = Literal[
    "DBIESSE",
    "DCYFLE",
    "DDRILL",
    "DFAM",
    "DMORBI",
    "DSPRIN",
]


@lru_cache
def load_edged_door_routings_config() -> dict[str, Any]:
    with EDGED_DOORS_ROUTINGS_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Edged door routings config must be a mapping.")

    required_keys = {"fragments", "templates"}

    missing_keys = required_keys - set(data)

    if missing_keys:
        raise ValueError(
            "Edged door routings config missing required keys: "
            f"{sorted(missing_keys)}"
        )

    if not isinstance(data["fragments"], dict):
        raise ValueError("'fragments' must be a mapping.")

    if not isinstance(data["templates"], dict):
        raise ValueError("'templates' must be a mapping.")

    return data


def get_edged_door_template_name(
    *,
    source_method: SourceMethod,
    destination: Destination,
) -> str:
    """
    Resolve frontend edged-door routing options to a template name.

    The actual template names live in YAML. This function only matches
    against template metadata.
    """

    config = load_edged_door_routings_config()
    templates = config["templates"]

    matches = []

    for template_name, template in templates.items():
        if template.get("source_method") != source_method:
            continue

        if template.get("destination") != destination:
            continue

        matches.append(template_name)

    if len(matches) == 1:
        return matches[0]

    if not matches:
        raise ValueError(
            "No edged door routing template found for: "
            f"{source_method=}, {destination=}"
        )

    raise ValueError(
        "Multiple edged door routing templates found for: "
        f"{source_method=}, {destination=}. "
        f"Matches: {sorted(matches)}"
    )


def _resolve_operation(
    *,
    operation: dict[str, Any],
    context: dict[str, Any],
    fragments: dict[str, Any],
) -> dict[str, Any] | None:
    if "work_centre" in operation:
        return operation.copy()

    if "work_centre_from_context" not in operation:
        raise ValueError(
            "Operation must contain either 'work_centre' or "
            "'work_centre_from_context'."
        )

    context_key = operation["work_centre_from_context"]
    lookup_name = operation["lookup"]

    if context_key not in context:
        raise ValueError(f"Missing context value: {context_key!r}")

    context_value = context[context_key]

    try:
        work_centre = fragments[lookup_name][context_value]
    except KeyError:
        raise ValueError(
            f"Unsupported {context_key!r} value {context_value!r} "
            f"for lookup {lookup_name!r}."
        ) from None

    if work_centre is None and operation.get("skip_if_null"):
        return None

    resolved = operation.copy()
    resolved.pop("work_centre_from_context")
    resolved.pop("lookup")
    resolved.pop("skip_if_null", None)
    resolved["work_centre"] = work_centre

    return resolved


def _get_fragment_operations(
    *,
    fragment: dict[str, Any],
    context: dict[str, Any],
    fragments: dict[str, Any],
) -> list[dict[str, Any]]:
    operations = fragment.get("operations")

    if not isinstance(operations, list):
        raise ValueError("Fragment must contain an 'operations' list.")

    resolved_operations = []

    for operation in operations:
        resolved_operation = _resolve_operation(
            operation=operation,
            context=context,
            fragments=fragments,
        )

        if resolved_operation is not None:
            resolved_operations.append(resolved_operation)

    return resolved_operations


def _insert_after_work_centre(
    *,
    operations: list[dict[str, Any]],
    insert_after: str,
    operation_to_insert: dict[str, Any],
) -> list[dict[str, Any]]:
    operations = operations.copy()

    for index, operation in enumerate(operations):
        if operation["work_centre"] == insert_after:
            operations.insert(index + 1, operation_to_insert)
            return operations

    raise ValueError(
        f"Cannot insert {operation_to_insert['work_centre']!r}; "
        f"{insert_after!r} is not present in resolved operations."
    )


def _insert_after_work_centre_prefix(
    *,
    operations: list[dict[str, Any]],
    insert_after_prefix: str,
    operation_to_insert: dict[str, Any],
) -> list[dict[str, Any]]:
    operations = operations.copy()

    for index, operation in enumerate(operations):
        if operation["work_centre"].startswith(insert_after_prefix):
            operations.insert(index + 1, operation_to_insert)
            return operations

    raise ValueError(
        f"Cannot insert {operation_to_insert['work_centre']!r}; "
        f"no work centre starts with {insert_after_prefix!r}."
    )


def _apply_drilling(
    *,
    operations: list[dict[str, Any]],
    destination: Destination,
    drilled: bool,
    production_drill_work_centre: ProductionDrillWorkCentre | None,
    fragments: dict[str, Any],
) -> list[dict[str, Any]]:
    if not drilled:
        return operations

    drilling_config = fragments["drilling"]

    if destination == "mto":
        mto_drilling = drilling_config["mto"]

        return _insert_after_work_centre(
            operations=operations,
            insert_after=mto_drilling["insert_after"],
            operation_to_insert={
                "work_centre": mto_drilling["work_centre"],
                "milestone": "Y",
            },
        )

    if production_drill_work_centre is None:
        raise ValueError(
            "production_drill_work_centre is required for drilled "
            "non-MTO edged doors."
        )

    if production_drill_work_centre not in drilling_config["production_work_centres"]:
        raise ValueError(
            "Unsupported production drill work centre: "
            f"{production_drill_work_centre!r}"
        )

    production_drilling = drilling_config["production"]

    return _insert_after_work_centre_prefix(
        operations=operations,
        insert_after_prefix=production_drilling["insert_after_prefix"],
        operation_to_insert={
            "work_centre": production_drill_work_centre,
            "milestone": "Y",
        },
    )


def resolve_edged_door_operations_template(
    *,
    template_name: str,
    context: dict[str, Any],
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

    source_method = template["source_method"]
    destination = template["destination"]

    resolved_ops: list[dict[str, Any]] = []

    source_fragment = fragments["source"][source_method]

    resolved_ops.extend(
        _get_fragment_operations(
            fragment=source_fragment,
            context=context,
            fragments=fragments,
        )
    )

    edging_fragment = fragments["edging"]

    resolved_ops.extend(
        _get_fragment_operations(
            fragment=edging_fragment,
            context=context,
            fragments=fragments,
        )
    )

    finish_fragment = fragments["finish"][destination]

    if destination == "mto":
        resolved_ops.extend(finish_fragment["pre_drilling_ops"])

        resolved_ops = _apply_drilling(
            operations=resolved_ops,
            destination=destination,
            drilled=bool(context.get("drilled", False)),
            production_drill_work_centre=context.get(
                "production_drill_work_centre"
            ),
            fragments=fragments,
        )

        resolved_ops.extend(finish_fragment["post_drilling_ops"])

    else:
        resolved_ops = _apply_drilling(
            operations=resolved_ops,
            destination=destination,
            drilled=bool(context.get("drilled", False)),
            production_drill_work_centre=context.get(
                "production_drill_work_centre"
            ),
            fragments=fragments,
        )

        resolved_ops.extend(
            _get_fragment_operations(
                fragment=finish_fragment,
                context=context,
                fragments=fragments,
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