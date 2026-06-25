from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml


JPULL_OPS_PATH = Path("config/data/routings/jayl_routings.yml")


BottomEdgeType = Literal["wrapped", "edged"]
Destination = Literal["stocked", "mto", "oem"]
ProductionDrillWorkCentre = Literal[
    "DBIESSE",
    "DCYFLE",
    "DDRILL",
    "DFAM",
    "DMORBI",
    "DSPRIN",
]
PackagingWorkCentre = Literal[
    "DCPKU1",
    "DCPKU2",
    "DPACKM",
]


def get_jpull_template_name(
    *,
    bottom_edge_type: BottomEdgeType,
    destination: Destination,
) -> str:
    config = load_jpull_operations_config()
    templates = config["templates"]

    matches = []

    for template_name, template in templates.items():
        if (
            template.get("edge_type") == bottom_edge_type
            and template.get("destination") == destination
        ):
            matches.append(template_name)

    if not matches:
        raise ValueError(
            f"No J-Pull routing template found for "
            f"{bottom_edge_type=}, {destination=}"
        )

    if len(matches) > 1:
        raise ValueError(
            f"Multiple J-Pull routing templates found for "
            f"{bottom_edge_type=}, {destination=}: {matches}"
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


def _get_fragment_operations(
    *,
    fragment: dict[str, Any],
) -> list[dict[str, Any]]:
    operations = fragment.get("operations")

    if not isinstance(operations, list):
        raise ValueError("Fragment must contain an 'operations' list.")

    return [operation.copy() for operation in operations]


def _insert_after_work_centre(
    *,
    operations: list[dict[str, Any]],
    insert_after: str,
    operation_to_insert: dict[str, Any],
) -> list[dict[str, Any]]:
    operations = [operation.copy() for operation in operations]

    for index, operation in enumerate(operations):
        if operation["work_centre"] == insert_after:
            operations.insert(index + 1, operation_to_insert.copy())
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
    operations = [operation.copy() for operation in operations]

    for index, operation in enumerate(operations):
        if operation["work_centre"].startswith(insert_after_prefix):
            operations.insert(index + 1, operation_to_insert.copy())
            return operations

    raise ValueError(
        f"Cannot insert {operation_to_insert['work_centre']!r}; "
        f"no work centre starts with {insert_after_prefix!r}."
    )


def _insert_before_work_centre(
    *,
    operations: list[dict[str, Any]],
    insert_before: str | list[str],
    operation_to_insert: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Insert an operation immediately after a specific work centre.

    A shallow copy of the operations list is created so that the original
    sequence remains unchanged. The first operation whose work centre
    exactly matches ``insert_before`` is used as the insertion point.

    An error is raised if the target work centre is not present, helping to
    detect configuration drift between insertion rules and routing
    fragments.
    """

    operations = operations.copy()

    for index, operation in enumerate(operations):
        if operation["work_centre"] == insert_before or operation["work_centre"] in insert_before:
            operations.insert(index, operation_to_insert)
            return operations

    raise ValueError(
        f"Cannot insert {operation_to_insert['work_centre']!r}; "
        f"{insert_before!r} is not present in resolved operations."
    )


def _replace_work_centre(
    *,
    operations: list[dict[str, Any]],
    replace: str | list[str],
    operation_to_insert: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Replace a specific work centre.

    A shallow copy of the operations list is created so that the original
    sequence remains unchanged. The first operation whose work centre
    exactly matches ``replace`` is used as the insertion point.

    An error is raised if the target work centre is not present, helping to
    detect configuration drift between insertion rules and routing
    fragments.
    """

    operations = operations.copy()

    for index, operation in enumerate(operations):
        if operation["work_centre"] == replace or operation["work_centre"] in replace:
            operations[index] = operation_to_insert
            return operations

    raise ValueError(
        f"Cannot insert {operation_to_insert['work_centre']!r}; "
        f"{replace!r} is not present in resolved operations."
    )


def _apply_drilling(
    *,
    operations: list[dict[str, Any]],
    destination: Destination,
    drilled: bool,
    packaged: bool,
    production_drill_work_centre: ProductionDrillWorkCentre | None,
    fragments: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Apply drilling operations to a resolved routing sequence.

    If drilling is not required, the operations are returned unchanged.
    Otherwise, the insertion strategy depends on the destination type:

    - MTO doors always use a fixed drilling work centre defined in the
    configuration and insert it at a specific point in the process.

    - Stocked and OEM doors require a production drilling work centre to be
    supplied at runtime. The selected work centre is validated against the
    configured list of supported machines before being inserted after the
    appropriate production-stage prefix.

    The returned list contains the original operations with any required
    drilling step inserted as a milestone operation.
    """

    if not drilled:
        return operations

    drilling_config = fragments["drilling"]

    production_drilling = drilling_config["production"]

    if destination == "mto":
        if packaged:
            return _insert_after_work_centre_prefix(
                operations=operations,
                insert_after_prefix=production_drilling["insert_after_prefix"],
                operation_to_insert={
                    "work_centre": production_drill_work_centre,
                    "milestone": "Y",
                },
            )
        else:
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

    return _insert_after_work_centre_prefix(
        operations=operations,
        insert_after_prefix=production_drilling["insert_after_prefix"],
        operation_to_insert={
            "work_centre": production_drill_work_centre,
            "milestone": "Y",
        },
    )


def _apply_packaging(
    *,
    operations: list[dict[str, Any]],
    destination: Destination,
    packaged: bool,
    packaging_work_centre: PackagingWorkCentre | None,
    fragments: dict[str, Any],
) -> list[dict[str, Any]]:
    
    if not packaged:
        return operations
    
    packaging_config = fragments["packaging"]

    if destination == "stocked":
        mto_packaging = packaging_config["stocked"]

        return _replace_work_centre(
            operations=operations,
            replace=mto_packaging["replace"],
            operation_to_insert={
                "work_centre": packaging_work_centre,
                "milestone": "Y",
            },
        )
    
    elif destination == "mto":
        mto_packaging = packaging_config["mto"]

        return _insert_before_work_centre(
            operations=operations,
            insert_before=mto_packaging["insert_before"],
            operation_to_insert={
                "work_centre": packaging_work_centre,
                "milestone": "Y",
            },
        )
    elif destination == "oem":
        mto_packaging = packaging_config["oem"]

        return _insert_before_work_centre(
            operations=operations,
            insert_before=mto_packaging["insert_before"],
            operation_to_insert={
                "work_centre": packaging_work_centre,
                "milestone": "Y",
            },
        )
    
    if packaging_work_centre is None:
        raise ValueError(
            "packaging_work_centre is required for drilled "
            "non-MTO edged doors."
        )
    
    if packaging_work_centre not in packaging_config["packaging_work_centres"]:
        raise ValueError(
            "Unsupported production packaging work centre: "
            f"{packaging_work_centre!r}"
        )


def resolve_jpull_operations_template(
    *,
    template_name: str,
    context: dict[str, Any],
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

    edge_type = template["edge_type"]
    destination = template["destination"]
    source = template["source"]

    resolved_ops: list[dict[str, Any]] = []

    resolved_ops.extend(
        _get_fragment_operations(
            fragment=fragments["source"][source],
        )
    )

    resolved_ops.extend(
        _get_fragment_operations(
            fragment=fragments["edging"][edge_type],
        )
    )

    resolved_ops.extend(
        _get_fragment_operations(
            fragment=fragments["shaping"]["standard"],
        )
    )

    finish_fragment = fragments["finish"][destination]

    if destination == "mto":
        resolved_ops.extend(
            [operation.copy() for operation in finish_fragment["pre_drilling_ops"]]
        )

        resolved_ops = _apply_drilling(
            operations=resolved_ops,
            destination=destination,
            drilled=bool(context.get("drilled", False)),
            packaged=bool(context.get("packaged", False)),
            production_drill_work_centre=context.get(
                "production_drill_work_centre"
            ),
            fragments=fragments,
        )

        resolved_ops.extend(
            [operation.copy() for operation in finish_fragment["post_drilling_ops"]]
        )

    else:
        resolved_ops = _apply_drilling(
            operations=resolved_ops,
            destination=destination,
            drilled=bool(context.get("drilled", False)),
            packaged=bool(context.get("packaged", False)),
            production_drill_work_centre=context.get(
                "production_drill_work_centre"
            ),
            fragments=fragments,
        )

        resolved_ops.extend(
            _get_fragment_operations(
                fragment=finish_fragment,
            )
        )

    resolved_ops = _apply_packaging(
        operations=resolved_ops,
        destination=destination,
        packaged=bool(context.get("packaged", False)),
        packaging_work_centre=context.get(
            "packaging_work_centre"
        ),
        fragments=fragments,
    )

    return [
        {
            "operation": index,
            "work_centre": op["work_centre"],
            "milestone": op["milestone"],
        }
        for index, op in enumerate(resolved_ops, start=1)
    ]