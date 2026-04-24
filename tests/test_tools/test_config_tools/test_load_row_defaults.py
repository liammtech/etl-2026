from tools.config_tools.config_loader import load_row_defaults
from pprint import pprint

def test_load_row_defaults():
    bom_def = load_row_defaults(table_name="BomStructure")
    pprint(bom_def)