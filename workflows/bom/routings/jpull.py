from typing import Literal

from config.loaders.routings.jpull import (
    get_jpull_template_name,
    resolve_jpull_operations_template,
)
from db.sql import append_multiple_records
from records.bom import build_bomoperations_row


def create_jpull_door_routing(
    *,
    stock_code: str,
    route: str,
    bottom_edge_type: Literal["wrapped", "edged"],
    destination: Literal["stocked", "mto", "oem"],
    drilled: bool,
    production_drill_work_centre: Literal[
        "DBIESSE",
        "DCYFLE",
        "DDRILL",
        "DFAM",
        "DMORBI",
        "DSPRIN",
    ] | None = None,
) -> None:
    template_name = get_jpull_template_name(
        bottom_edge_type=bottom_edge_type,
        destination=destination,
    )

    operations = resolve_jpull_operations_template(
        template_name=template_name,
        context={
            "drilled": drilled,
            "production_drill_work_centre": production_drill_work_centre,
        },
    )

    rows = [
        build_bomoperations_row(
            values={
                "StockCode": stock_code,
                "Route": route,
                "Operation": operation["operation"],
                "WorkCentre": operation["work_centre"],
                "Milestone": operation["milestone"],
            },
        )
        for operation in operations
    ]

    append_multiple_records(
        table="BomOperations",
        rows=rows,
    )