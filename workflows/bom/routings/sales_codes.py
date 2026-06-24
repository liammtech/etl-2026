from domain.bom.templates.routing_templates import create_routing_from_template


def create_std_sales_code_ops(stock_code: str, route: str) -> None:
    create_routing_from_template(
        stock_code=stock_code,
        route=route,
        template_name="standard_sales",
    )


def create_std_drilled_sales_code_ops(stock_code: str, route: str) -> None:
    create_routing_from_template(
        stock_code=stock_code,
        route=route,
        template_name="drilled_sales",
    )


def create_rigid_sales_code_ops(stock_code: str, route: str) -> None:
    create_routing_from_template(
        stock_code=stock_code,
        route=route,
        template_name="rigid_sales",
    )


def create_rigid_drilled_sales_code_ops(stock_code: str, route: str) -> None:
    create_routing_from_template(
        stock_code=stock_code,
        route=route,
        template_name="rigid_drilled_sales",
    )
