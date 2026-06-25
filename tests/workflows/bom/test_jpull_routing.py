from workflows.bom.routings.jpull import create_jpull_door_routing

def test():
    create_jpull_door_routing(
        stock_code="JAYL002",
        route=0,
        bottom_edge_type="wrapped",
        drilled=True,
        destination="oem",
        production_drill_work_centre="DCYFLE"
    )