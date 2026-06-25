from workflows.bom.routings.pressed import create_pressed_door_routing

def test():
    create_pressed_door_routing(
        stock_code="PRESS003",
        route=0,
        construction="standard",
        destination="industrial",
        main_thickness=18,
        drilled=True,
        production_drill_work_centre="DCYFLE",
        production_drill_position="post_press"
    )