from workflows.bom.routings import create_std_cabinet_routing

def test():
    create_std_cabinet_routing(
        stock_code="NBWMISC600",
        route=0
    )