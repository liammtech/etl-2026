# config/loaders/routings/pressed.py

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml


CONFIG_PATH = Path("config/routings/pressed.yml")


Construction = Literal["standard", "plant_on", "plant_in"]
Destination = Literal["industrial", "stocked", "mto"]
DrillPosition = Literal["pre_press", "post_press"]


def get_pressed_door_template_name(
    *,
    construction: Construction,
    destination: Destination,
) -> str:
    template_names = {
        ("standard", "industrial"): "standard_industrial",
        ("standard", "stocked"): "standard_stocked",
        ("standard", "mto"): "standard_mto",
        ("plant_on", "industrial"): "plant_on_industrial",
        ("plant_on", "stocked"): "plant_on_stocked",
        ("plant_on", "mto"): "plant_on_mto",
        ("plant_in", "industrial"): "plant_in_industrial",
        ("plant_in", "stocked"): "plant_in_stocked",
        ("plant_in", "mto"): "plant_in_mto",
    }

    try:
        return template_names[(construction, destination)]
    except KeyError:
        raise ValueError(
            "Unsupported pressed door routing combination: "
            f"construction={construction!r}, destination={destination!r}"
        )


@lru_cache
def load_pressed_door_routings_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _get_fragment_operations(
    *,
    fragment_name: str,
) -> list[str]:
    config = load_pressed_door_routings_config()
    fragments = config["fragments"]

    try:
        fragment = fragments[fragment_name]
    except KeyError:
        raise ValueError(f"Unknown pressed door routing fragment: {fragment_name!r}")

    if not isinstance(fragment, list):
        raise TypeError(
            f"Pressed door routing fragment {fragment_name!r} is not an operations list"
        )

    return fragment.copy()


def _get_saw_work_centre(
    *,
    thickness: int,
) -> str:
    config = load_pressed_door_routings_config()
    saw_work_centres = config["fragments"]["saw_work_centres"]

    try:
        return saw_work_centres[thickness]
    except KeyError:
        raise ValueError(f"No DSAW work centre configured for thickness: {thickness!r}")


def _get_construction_fragment(
    *,
    construction: str,
) -> dict[str, Any]:
    config = load_pressed_door_routings_config()

    try:
        return config["fragments"]["constructions"][construction]
    except KeyError:
        raise ValueError(f"Unsupported pressed door construction: {construction!r}")


def _get_destination_fragment(
    *,
    destination: str,
) -> dict[str, Any]:
    config = load_pressed_door_routings_config()

    try:
        return config["fragments"]["destinations"][destination]
    except KeyError:
        raise ValueError(f"Unsupported pressed door destination: {destination!r}")


def _get_template(
    *,
    template_name: str,
) -> dict[str, str]:
    config = load_pressed_door_routings_config()

    try:
        return config["templates"][template_name]
    except KeyError:
        raise ValueError(f"Unsupported pressed door routing template: {template_name!r}")


def _insert_after(
    *,
    operations: list[str],
    insert_after: str,
    work_centre: str,
) -> list[str]:
    operations = operations.copy()

    try:
        index = operations.index(insert_after)
    except ValueError:
        raise ValueError(
            f"Cannot insert {work_centre!r}; {insert_after!r} is not in operations"
        )

    operations.insert(index + 1, work_centre)
    return operations


def _resolve_saw_operations(
    *,
    construction_fragment: dict[str, Any],
    main_thickness: int,
    overlay_thickness: int | None = None,
) -> list[str]:
    thickness_values = {
        "main_thickness": main_thickness,
        "overlay_thickness": overlay_thickness,
    }

    saw_operations = []

    for layer in construction_fragment["layers"]:
        thickness_field = layer["thickness_field"]
        thickness = thickness_values[thickness_field]

        if thickness is None:
            raise ValueError(
                f"Missing thickness value for pressed door layer: {thickness_field!r}"
            )

        if layer.get("require_single_digit") and thickness >= 10:
            raise ValueError(
                f"{thickness_field!r} must be single digit for this construction; "
                f"got {thickness!r}"
            )

        saw_operations.append(_get_saw_work_centre(thickness=thickness))

    return saw_operations


def _apply_drilling(
    *,
    operations: list[str],
    destination: str,
    drilled: bool,
    production_drill_work_centre: str | None = None,
    production_drill_position: DrillPosition | None = None,
) -> list[str]:
    if not drilled:
        return operations

    config = load_pressed_door_routings_config()
    drilling = config["fragments"]["drilling"]

    if destination == "mto":
        mto_drilling = drilling["mto"]

        return _insert_after(
            operations=operations,
            insert_after=mto_drilling["insert_after"],
            work_centre=mto_drilling["work_centre"],
        )

    if production_drill_work_centre is None:
        raise ValueError("production_drill_work_centre is required for drilled non-MTO pressed doors")

    if production_drill_position is None:
        raise ValueError("production_drill_position is required for drilled non-MTO pressed doors")

    if production_drill_work_centre not in drilling["production_work_centres"]:
        raise ValueError(
            "Unsupported production drill work centre: "
            f"{production_drill_work_centre!r}"
        )

    try:
        position_config = drilling["production_positions"][production_drill_position]
    except KeyError:
        raise ValueError(
            f"Unsupported production drill position: {production_drill_position!r}"
        )

    return _insert_after(
        operations=operations,
        insert_after=position_config["insert_after"],
        work_centre=production_drill_work_centre,
    )


def resolve_pressed_door_operations_template(
    *,
    template_name: str,
    main_thickness: int,
    overlay_thickness: int | None = None,
    drilled: bool = False,
    production_drill_work_centre: str | None = None,
    production_drill_position: DrillPosition | None = None,
) -> list[str]:
    template = _get_template(template_name=template_name)

    construction = template["construction"]
    destination = template["destination"]

    construction_fragment = _get_construction_fragment(construction=construction)
    destination_fragment = _get_destination_fragment(destination=destination)

    operations = []

    operations.extend(
        _resolve_saw_operations(
            construction_fragment=construction_fragment,
            main_thickness=main_thickness,
            overlay_thickness=overlay_thickness,
        )
    )

    operations.extend(construction_fragment["pre_pressing_ops"])
    operations.extend(_get_fragment_operations(fragment_name="common_pressing_flow"))

    if destination == "mto":
        operations.extend(destination_fragment["pre_drilling_ops"])

    operations = _apply_drilling(
        operations=operations,
        destination=destination,
        drilled=drilled,
        production_drill_work_centre=production_drill_work_centre,
        production_drill_position=production_drill_position,
    )

    if destination == "mto":
        operations.extend(destination_fragment["post_drilling_ops"])
    else:
        operations.extend(destination_fragment["ending_ops"])

    return operations