from math import floor

def calculate_jpull_bar_qty(
    *,
    door_height: float,
    door_width: float,
    bar_width: float = 2100,
    jpull_direction: str = "Horizontal"
) -> float:
    
    print(f"Bar width data type: {type(bar_width)}")
    print(f"Door height data type: {type(door_height)}")
    door_height_over = door_height + 5
    print("{floor(bar_width / door_height_over)}")

    if jpull_direction == "Vertical":
        
        mpj_qty_per = (
            1 / floor(bar_width / door_height_over)
        )
    else:
        mpj_qty_per = (
            1 / floor(bar_width / door_height_over)           
        )

    return mpj_qty_per

# All other calculations are exactly as per Cut and Edged, use functions from
# tools.calculations.edged_qty_per_calcs