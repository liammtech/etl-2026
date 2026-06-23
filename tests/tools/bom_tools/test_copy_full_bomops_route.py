from tools.bom_tools.bom_organisation import copy_full_bomops_route

def test_copy_bomops():
    copy_full_bomops_route(
        source_stock_code="SWCC012",
        source_route="1",
        dest_route="1"
    )