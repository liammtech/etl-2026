from tools.bom_tools.bom_organisation import defrag_routing

def test_defrag_routing():
    defrag_routing(
        stock_code="PJMW895X296",
        route=0
    )