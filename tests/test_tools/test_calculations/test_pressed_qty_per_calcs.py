import pytest
from tools.calculations.pressed_qty_per_calcs import calculate_mel_board_qty, calculate_glue_qty, calculate_glue_hardener_qty


def test_mel_calc():
    calculate_mel_board_qty(
        door_height=345,
        door_width=389,
        board_height=2620,
        board_width=2070
    )

    
def test_glue_calc():
    calculate_glue_qty(
        door_height=345,
        door_width=389
    )


def test_glue_hardener_calc():
    calculate_glue_hardener_qty(
        door_height=345,
        door_width=389
    )