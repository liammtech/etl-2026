import yaml
from pathlib import Path
from typing import Any


def _load_yaml_section(
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


def _load_yaml(config_filepath: str) -> dict[str, Any]:
    path = Path(__file__).parent.parent.parent / config_filepath
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _get_value_from_grouped_yaml(
    *,
    config_filepath: str,
    lookup_key: str,
    group_name: str | None = None,
    group_suffix: str = ""
) -> Any:
    data = _load_yaml(config_filepath)

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
    data = _load_yaml(config_filepath)
    return data[lookup_key]


def load_row_defaults(table_name: str) -> dict:
    table_name = table_name.lower().replace("+", "plus").replace("[","").replace("]", "")

    return _load_yaml_section(
        config_filepath=f"config/defaults/{table_name}_defaults.yml",
        section_name=f"{table_name}_defaults"
    )



def get_colour_from_prefix(
    sku_prefix: str,
    table_name: str | None = None
) -> str:
    return _get_value_from_grouped_yaml(
        config_filepath="config/validation/colour_prefixes.yml",
        lookup_key=sku_prefix,
        group_name=table_name,
        group_suffix="_colours"
    )


def get_material_via_range_colour(
    range: str,
    material: str,
    colour: str
) -> str:
    return _get_value_from_grouped_yaml(
        config_filepath=f"config/materials/{range}_materials.yml",
        lookup_key=colour,
        group_name=material
    )


def get_material_via_dimension(
    range: str,
    material: str,
    dimension: str        
) -> str:
    return _get_value_from_grouped_yaml(
        config_filepath=f"config/materials/{range}_materials.yml",
        lookup_key=dimension,
        group_name=material
    )
