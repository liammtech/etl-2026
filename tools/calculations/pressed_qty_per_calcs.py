def calculate_mel_board_qty(
    *,
    door_height: float,
    door_width: float,
    board_height: float,
    board_width: float,
    board_waste: float = 0.08 # Standard waste, almost never changes
) -> float:
    mel_qty_per = (((door_height + 8) * (door_width + 8)) / (1 - board_waste)) / (board_height * board_width)

    mel_qty_per = round(mel_qty_per, 6)
    print(f"\nMEL calc result is {mel_qty_per} PCS")
    return mel_qty_per

def calculate_glue_qty(
    door_height: float,
    door_width: float,
    door_depth: float = 18
):
    glue_qty_per = (
        (((door_height / 1000) +
        ((2 * door_depth) / 1000)) *
        ((door_width / 1000) + 
        ((2 * door_depth) / 1000)) * 0.08) / 6 * 5
    )

    glue_qty_per = round(glue_qty_per, 6)
    print(f"\nGL100 calc result is {glue_qty_per} KG")
    return glue_qty_per

def calculate_glue_hardener_qty(
    door_height: float,
    door_width: float,
    door_depth: float = 18
):
    glue_qty_per = (
        (((door_height / 1000) +
        ((2 * door_depth) / 1000)) *
        ((door_width / 1000) + 
        ((2 * door_depth) / 1000)) * 0.08) / 6
    )

    glue_qty_per = round(glue_qty_per, 6)
    print(f"\nGL101 calc result is {glue_qty_per} KG")
    return glue_qty_per

def calculate_foil_qty():
    pass

def calculate_pallet_qty():
    pass