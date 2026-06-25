from workflows.bom.routings.edged import create_edged_door_routing

def test():
    create_edged_door_routing(
        stock_code="EDGED011",
        route=0,
        source_method="nest",
        edge_count=4,
        destination="mto",
        drilled=True,
        packaged=True,
        thickness="18mm",
        pallet_type="long_pallet",
        production_drill_work_centre="DCYFLE",
        packaging_work_centre="DCPKU2"
    )