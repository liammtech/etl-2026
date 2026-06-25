from workflows.bom.routings.edged import create_edged_door_routing

def test():
    create_edged_door_routing(
        stock_code="EDGED004",
        route=0,
        source_method="rout",
        edge_count=2,
        destination="oem",
        drilled=True,
        thickness="16mm",
        pallet_type="long_pallet",
        production_drill_work_centre="DCYFLE"
    )