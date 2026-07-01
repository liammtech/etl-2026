from workflows.bom.routings.pressed import create_pressed_door_routing

def test():
    create_pressed_door_routing(
        stock_code="PRESS004",
        route=0,
        construction="standard",
        destination="mto",
        main_thickness=18,
        drilled=True,
        packaged=True,
        production_drill_work_centre="DCYFLE",
        production_drill_position="post_press",
        packaging_work_centre="DCPKU2"
    )