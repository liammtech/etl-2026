def calculate_lldr_board_qty(
    *,
    door_height: float,
    door_width: float,
    board_height: float,
    board_width: float,
    board_waste: float = 0.13 # Standard waste, almost never changes
) -> float:
    print(f"Full board M2: {board_height * board_width}")
    print(door_height)
    print(door_width)
    print(board_height)
    print(board_width)
    print(board_waste)
    zlam_qty_per = (
        ((door_height + 8) * (door_width + 8) * (1 + board_waste)) /
        (board_height * board_width)
    )

    zlam_qty_per + round(zlam_qty_per, 6)
    print(f"\nZLAM calc result is {zlam_qty_per} PCS")
    return zlam_qty_per

def calculate_edging_qty(
    *,
    door_height: float,
    door_width: float,
    height_sides_edged: float,
    width_sides_edged: float
) -> float:
    edging_qty_per = (
        (((door_height + 20) / 1000) * height_sides_edged) +
        (((door_width + 20) / 1000) * width_sides_edged)
    )
    edging_qty_per + round(edging_qty_per, 6)
    print(f"Edging calc result is {edging_qty_per} LM")
    return edging_qty_per

def calculate_glue_qty(
    *,
    door_height: float,
    door_width: float,
    door_thickness: float,
    height_sides_edged: float,
    width_sides_edged: float
) -> float:
    lm_to_edge = (
        ((door_height * height_sides_edged) / 1000) +
        ((door_width * width_sides_edged) / 1000)
    )
    glue_area_m2 = lm_to_edge * (door_thickness / 1000)
    glue_qty_per = round((glue_area_m2 * 0.05), 6)
    return glue_qty_per

def calculate_pallet_qty(
    *,
    pallet_max_qty: float
) -> float:
    pallet_qty_per = round((1 / pallet_max_qty), 6)
    print(f"\nPallet qty calc result is {pallet_qty_per} PCS")
    return pallet_qty_per

def calculate_layflat_qty(
    *,
    door_height: float,
    door_width: float,
    door_thickness: float    
) -> float:
    pass
    # (longest side + door thickness + 40) /1000
    longest_side = door_height if door_height > door_width else door_width
    layflat_qty_per = (
        (longest_side + door_thickness + 40) / 1000
    )
    layflat_qty_per = round(layflat_qty_per, 6)
    return layflat_qty_per