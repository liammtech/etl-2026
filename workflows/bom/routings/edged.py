from typing import Literal

from config.loaders.routings.edged import (
    get_edged_door_template_name,
    resolve_edged_door_operations_template,
)
from db.sql import append_multiple_records
from records.bom import build_bomoperations_row


def create_edged_door_routing(
    *,
    stock_code: str,
    route: str,
    source_method: Literal["nest", "rout"],
    edge_count: Literal[0, 1, 2, 3, 4],
    destination: Literal["stocked", "mto", "oem"],
    drilled: bool,
    thickness: Literal[
        "3mm",
        "4mm",
        "6mm",
        "7mm",
        "8mm",
        "9mm",
        "12mm",
        "15mm",
        "16mm",
        "18mm",
        "19mm",
        "22mm",
        "25mm",
    ],
    pallet_type: Literal["standard_pallet", "long_pallet"] = "standard_pallet",
) -> None:
    template_name = get_edged_door_template_name(
        source_method=source_method,
        destination=destination,
        drilled=drilled,
    )

    operations = resolve_edged_door_operations_template(
        template_name=template_name,
        context={
            "thickness": thickness,
            "edge_count": str(edge_count),
            "pallet_type": pallet_type,
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