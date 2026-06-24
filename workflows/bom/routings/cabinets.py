from domain.bom.templates.routing_templates import create_routing_from_template


def create_std_cabinet_routing(stock_code: str, route: str) -> None:
    create_routing_from_template(
        stock_code=stock_code,
        route=route,
        template_name="standard_cab",
    )