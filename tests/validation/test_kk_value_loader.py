from tools.config_tools.config_loader import get_kitchen_kit_values
from pprint import pprint

def test_get_kitchen_kit_values():
    vals = get_kitchen_kit_values(value_group="door-sizes")
    pprint(vals)
