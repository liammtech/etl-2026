import yaml
from pathlib import Path
from typing import Any


def load_yaml_section(
    *,
    config_filepath: str,
    section_name: str | None = None
) -> dict:
    path = Path(__file__).parent.parent.parent / config_filepath

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    print(data)
    if section_name is None:
        return data

    return data[section_name]


def load_yaml(config_filepath: str) -> dict[str, Any]:
    path = Path(__file__).parent.parent.parent / config_filepath
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def get_value_from_grouped_yaml(
    *,
    config_filepath: str,
    lookup_key: str,
    group_name: str | None = None,
    group_suffix: str = ""
) -> Any:
    data = load_yaml(config_filepath)

    if group_name is not None:
        group_key = f"{group_name.lower()}{group_suffix}"
        return data[group_key][lookup_key]

    for group_values in data.values():
        if lookup_key in group_values:
            return group_values[lookup_key]

    raise KeyError(f"No value found for key: {lookup_key}")


def get_config_constant_value(    
    *,
    config_filepath: str,
    lookup_key: str,
) -> str:
    data = load_yaml(config_filepath)
    return data[lookup_key]