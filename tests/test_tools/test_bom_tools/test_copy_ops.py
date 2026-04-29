from tools.bom_tools.bom_organisation import copy_bomops_to_new_route

def test_copy_ops():
    copy_bomops_to_new_route(
        source_route="5",
        source_stock_code="PJMW895X296",
        dest_route="T",
        dest_stock_code="PJMW895X296"
    )