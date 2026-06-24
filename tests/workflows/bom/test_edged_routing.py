from workflows.bom.routings.edged import create_edged_door_routing

def test():
    create_edged_door_routing(
        stock_code="EDGEDCODE2",
        route=5,
        source_method="rout",
        edge_count=3,
        destination="mto",
        drilled=False,
        thickness="18mm",
        pallet_type="standard_pallet"
    )