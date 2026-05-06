from tools.sku_tools.fix_volumetrics import fix_door_volumetrics
from pprint import pprint

def test_build_bm_row():
    fix_door_volumetrics(stock_code="MCCBS101")
