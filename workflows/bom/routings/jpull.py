from typing import Literal

from config.loaders.routings.jpull import (
    get_jpull_template_name,
    resolve_jpull_operations_template,
)
from db.sql import append_multiple_records
from records.bom import build_bomoperations_row


def create_jpull_routing(
    *,
    stock_code: str,
    route: str,
    edge_type: Literal["wrapped", "edged"],
    drilled: bool,
    destination: Literal["stocked", "mto", "oem"],
) -> None:
    """
    Create a J-Pull BomOperations routing.

    Args:
        stock_code:
            Stock code receiving the routing.

        route:
            Syspro route.

        edge_type:
            wrapped
            edged

        drilled:
            Whether drilling operations should be included.

        destination:
            stocked
            mto
            oem
    """

    template_name = get_jpull_template_name(
        edge_type=edge_type,
        drilled=drilled,
        destination=destination,
    )

    operations = resolve_jpull_operations_template(
        template_name=template_name
    )

    rows = []

    for operation in operations:

        rows.append(
            build_bomoperations_row(
                values={
                    "StockCode": stock_code,
                    "Route": route,
                    "Operation": operation["operation"],
                    "WorkCentre": operation["work_centre"],
                    "Milestone": operation["milestone"],
                },
            )
        )

    append_multiple_records(
        table="BomOperations",
        rows=rows,
    )