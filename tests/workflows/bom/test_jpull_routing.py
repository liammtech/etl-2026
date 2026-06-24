from workflows.bom.routings.jpull import create_jpull_routing

def test():
    create_jpull_routing(
        stock_code="JPULLCODE",
        route=0,
        edge_type="edged",
        drilled=True,
        destination="mto"
    )