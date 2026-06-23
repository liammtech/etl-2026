from records.bom import build_bomoperations_row
import db.sql as sql

def create_sales_code_ops(
    *,
    stock_code: str,
    route: str,
    recipe_name: str = "standard_sales",
) -> None:
    template = load_routing_template(recipe_name)

    rows = [
        build_bomoperations_row(
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

    sql.append_multiple_records(
        table="BomOperations",
        rows=rows,
    )