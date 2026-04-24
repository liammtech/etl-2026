from tools.row_builders import build_single_bomstructure_row
from pprint import pprint

def test_build_bm_row():
    row = build_single_bomstructure_row(
        parent_part="BLOB",
        component="BRPP",
        overlays={
            "QtyPer": 1,
            "QtyPerEnt": 1,
            "InclKitIssues": "N"
        }
    )
    pprint(row)