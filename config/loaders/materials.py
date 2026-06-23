from typing import Any

from config.loaders.yaml_loader import get_value_from_grouped_yaml, load_yaml


def get_material_via_range_colour(
    product_range: str,
    material: str,
    colour: str,
) -> str:
    """Get a material stock code from product range, material type, and colour."""
    return get_value_from_grouped_yaml(
        config_filepath=f"config/data/materials/{product_range}_materials.yml",
        lookup_key=colour,
        group_name=material,
    )


def get_material_via_dimension(
    product_range: str,
    material: str,
    dimension: str,
) -> str:
    """Get a material stock code from product range, material type, and dimension."""
    return get_value_from_grouped_yaml(
        config_filepath=f"config/data/materials/{product_range}_materials.yml",
        lookup_key=dimension,
        group_name=material,
    )


def get_pallets() -> Any:
    """Load pallet material configuration."""
    return load_yaml("config/data/materials/pallets.yml")