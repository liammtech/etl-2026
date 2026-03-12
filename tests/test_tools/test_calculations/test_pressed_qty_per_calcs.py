import pytest
import tools.calculations.pressed_qty_per_calcs as pressed

def test_mel_calc():
    pressed.calculate_mel_board_qty(
        door_height=345,
        door_width=389,
        board_height=2620,
        board_width=2070
    )

    
def test_glue_calc():
    pressed.calculate_glue_qty(
        door_height=345,
        door_width=389
    )


def test_glue_hardener_calc():
    pressed.calculate_glue_hardener_qty(
        door_height=345,
        door_width=389
    )
    

def test_foil_calc():
    pressed.calculate_foil_qty(
        door_height=345,
        door_width=389,
        foil_width=1420
    )

def test_pallet_calc():
    pressed.calculate_pallet_qty(
        pallet_max_qty=240
    )