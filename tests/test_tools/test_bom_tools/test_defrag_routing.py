from tools.bom_tools.bom_organisation import defrag_routing

def test_defrag_routing():
    defrag_routing(
        stock_code="JKKD04283X496",
        route="T"
    )