def calculate_centre_panel_board_qty(
    *,
    door_height: float,
    door_width: float,
    board_height: float,
    board_width: float,
    # door_shoulder_width: float = 65, # TODO: refine relevant variables for readability
    groove_offset: float = 111,
    board_waste: float = 0.13 # Standard waste, almost never changes
) -> float:
    
    zlam_qty_per = (
        ((door_height - groove_offset) * (door_width - groove_offset) * (1 + board_waste)) /
        (board_height * board_width)
    )

    zlam_qty_per = round(zlam_qty_per, 6)
    return zlam_qty_per


def calculate_cut_rail_qty(
    finished_rail_width: float,
    precut_rail_width: float = 1218
) -> float:
    
    rail_qty = round(precut_rail_width / finished_rail_width, 0)

    return rail_qty