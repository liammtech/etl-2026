from typing import Literal

from config.loaders.routings.pressed import (
    get_pressed_door_template_name,
    resolve_pressed_door_operations_template,
)
from db.sql import append_multiple_records
from records.bom import build_bomoperations_row


def create_pressed_door_routing(
    *,
    stock_code: str,
    route: str,
    construction: Literal["standard", "plant_on", "plant_in"],
    destination: Literal["industrial", "stocked", "mto"],
    main_thickness: int,
    drilled: bool,
    packaged: bool,
    overlay_thickness: int | None = None,
    production_drill_work_centre: Literal[
        "DBIESSE",
        "DCYFLE",
        "DDRILL",
        "DFAM",
        "DMORBI",
        "DSPRIN",
    ] | None = None,
    production_drill_position: Literal["pre_press", "post_press"] | None = None,
    packaging_work_centre: Literal[
        "DCPKU1",
        "DCPKU2",
        "DPACKM",
    ]
) -> None:
    template_name = get_pressed_door_template_name(
        construction=construction,
        destination=destination,
    )

    operations = resolve_pressed_door_operations_template(
        template_name=template_name,
        main_thickness=main_thickness,
        overlay_thickness=overlay_thickness,
        drilled=drilled,
        packaged=packaged,
        production_drill_work_centre=production_drill_work_centre,
        production_drill_position=production_drill_position,
        packaging_work_centre=packaging_work_centre,
    )

    rows = [
        build_bomoperations_row(
            values={
                "StockCode": stock_code,
                "Route": route,
                "Operation": operation_number,
                "WorkCentre": work_centre,
                "Milestone": "Y",
            },
        )
        for operation_number, work_centre in enumerate(operations, start=1)
    ]

    append_multiple_records(
        table="BomOperations",
        rows=rows,
    )