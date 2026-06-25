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
PackagingWorkCentre = Literal[
    "DCPKU1",
    "DCPKU2",
    "DPACKM",
]


@lru_cache
def load_edged_door_routings_config() -> dict[str, Any]:
    """
    Load, validate, and cache the edged-door routing configuration.

    The configuration file is expected to contain two top-level sections:

    - fragments:
        Reusable groups of operations, lookup tables, and insertion rules
        that can be combined to build complete routings.

    - templates:
        High-level routing definitions that describe which fragments should
        be used for a particular combination of source method and destination.

    Validation is performed when the file is first loaded to ensure the
    overall YAML structure matches the expectations of the resolver layer.
    Subsequent calls return the cached result without re-reading the file.
    """

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
    Resolve frontend edged-door options to a routing template name.

    Templates are selected by matching their YAML metadata rather than by
    hard-coded mappings in Python. The resolver searches all configured
    templates and returns the single template whose source method and
    destination match the supplied criteria.

    An error is raised if no matching template exists, or if multiple
    templates satisfy the same combination, ensuring that routing
    definitions remain unambiguous.
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
    """
    Resolve a single operation definition into a concrete work centre.

    Operations may either define a fixed work centre directly, or specify
    that the work centre should be selected from a lookup table using a
    runtime context value. Context-driven operations are expanded into a
    standard operation dictionary before being returned.

    If a lookup resolves to None and the operation is marked with
    ``skip_if_null``, the operation is omitted entirely by returning None.
    """

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
    """
    Resolve all operations within a routing fragment.

    Each operation definition is passed through the operation resolver so
    that context-dependent work centres are converted into concrete values.
    Operations that explicitly resolve to None are omitted, allowing
    fragments to define conditional steps that are skipped for certain
    configurations.

    The returned list contains only fully resolved operations that are
    ready to be combined into a complete routing template.
    """

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
    """
    Insert an operation immediately after a specific work centre.

    A shallow copy of the operations list is created so that the original
    sequence remains unchanged. The first operation whose work centre
    exactly matches ``insert_after`` is used as the insertion point.

    An error is raised if the target work centre is not present, helping to
    detect configuration drift between insertion rules and routing
    fragments.
    """

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
    """
    Insert an operation immediately after the first work centre that matches
    a given prefix.

    This allows insertion rules to target groups of related work centres
    without depending on a specific machine code. A shallow copy of the
    operations list is created so that the original sequence remains
    unchanged.

    An error is raised if no resolved work centre begins with the specified
    prefix, ensuring that routing assumptions remain valid as configuration
    changes over time.
    """

    operations = operations.copy()

    for index, operation in enumerate(operations):
        if operation["work_centre"].startswith(insert_after_prefix):
            operations.insert(index + 1, operation_to_insert)
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


def resolve_edged_door_operations_template(
    *,
    template_name: str,
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Resolve a named edged-door routing template into a numbered operations list.

    The template determines the high-level routing shape by selecting source,
    edging, and finish fragments from the YAML configuration. Each fragment is
    resolved using the supplied context so that any conditional or
    context-driven work centres are converted into concrete operations.

    Drilling is inserted as a separate step when requested. MTO templates place
    drilling between their configured pre- and post-drilling finish operations,
    while stocked and OEM templates apply drilling before the final finish
    fragment is appended.

    The returned list is normalised into the final routing shape expected by
    the caller, with sequential operation numbers assigned from 1.
    """

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

    print(f"Resolved ops start: {resolved_ops}")

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
            packaged=bool(context.get("packaged", False)),
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
            packaged=bool(context.get("packaged", False)),
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