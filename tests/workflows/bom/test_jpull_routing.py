from workflows.bom.routings.jpull import create_jpull_door_routing

def test():
    create_jpull_door_routing(
        stock_code="JAYL006",
        route=0,
        bottom_edge_type="wrapped",
        drilled=True,
        packaged=True,
        destination="mto",
        production_drill_work_centre="DCYFLE",
        packaging_work_centre="DCPKU1"
    )