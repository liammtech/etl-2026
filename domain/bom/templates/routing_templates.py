# domain/bom/routing_templates.py

import db.sql as sql
from config.loaders.routings.general import get_routing_template
from records import bom


def build_bomoperation_rows_from_template(
    *,
    stock_code: str,
    route: str,
    template_name: str,
) -> list[dict]:
    """Build BomOperations rows from a named routing template."""

    template = get_routing_template(template_name)

    return [
        bom.build_bomoperations_row(
            values={
                "StockCode": stock_code,
                "Route": route,
                "Operation": op["operation"],
                "WorkCentre": op["work_centre"],
                "Milestone": op["milestone"],
            }
        )
        for op in template
    ]


def create_routing_from_template(
    *,
    stock_code: str,
    route: str,
    template_name: str,
) -> None:
    """Create BomOperations rows from a named routing template."""

    rows = build_bomoperation_rows_from_template(
        stock_code=stock_code,
        route=route,
        template_name=template_name,
    )

    sql.append_multiple_records(
        table="BomOperations",
        rows=rows,
    )