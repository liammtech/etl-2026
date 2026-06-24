from workflows.bom.routings.edged import create_edged_door_routing

def test():
    create_edged_door_routing(
        stock_code="EDGEDCODE5",
        route=5,
        source_method="rout",
        edge_count=4,
        destination="mto",
        drilled=False,
        thickness="18mm",
        pallet_type="standard_pallet"
    )