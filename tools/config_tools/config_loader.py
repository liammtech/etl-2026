import yaml
from pathlib import Path

def load_row_defaults(table_name: str) -> dict:
    table_name = table_name.lower()
    # print(f"Table name is: {table_name}")

    config_filepath = f"config/table_defaults/{table_name}_defaults.yml"
    yaml_header = f"{table_name}_defaults"

    path = Path(__file__).parent.parent.parent / config_filepath
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data[yaml_header]