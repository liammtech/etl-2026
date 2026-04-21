from collections.abc import Callable
from tools import sql
from pathlib import Path
import yaml

class RecordNotFoundError(Exception):
    """Raised when a specific record is not found in the database."""
    pass

def get_jpull_direction(
    *,
    stock_code: str
) -> str:
    
    jpull_direction = sql.get_single_record(
        table="[InvMaster+]",
        criteria={
            "StockCode": stock_code
        },
        return_columns=["Jpull"]
    )

    jpull_direction = jpull_direction[0]
    print(f"J-Pull direction is {jpull_direction}")
    return jpull_direction
    
    
def find_correct_jpull_deban_op(
    *,
    stock_code: str, # Must be specific stock code
    jpull_direction: str = "Horizontal"
):
    door_dims = sql.get_single_record(
        table="zInvExtra",
        criteria={
            "StockCode": stock_code
        },
        return_columns=["Height","Width"]
    )

    jpull_direction = get_jpull_direction(stock_code=stock_code)

    print(type(door_dims))
    if jpull_direction == "Vertical":
        bar_dim = int(door_dims.Width)
    else:
        bar_dim = int(door_dims.Height)

    print(bar_dim)
    
    if bar_dim in [355, 390, 570, 715, 895, 1245]:
        edgebanding_op = "DEBAN2"
    else:
        edgebanding_op = "DEBAN3"

    print(edgebanding_op)
    return edgebanding_op