from domain.bom.analysis import get_range_modal_component

def test():
    get_range_modal_component(
        stock_code_prefix="ORAGW*",
        component_prefixes="GL*"
    )
