# config/validation/colours.py

from config.loaders.yaml_loader import get_value_from_grouped_yaml


def get_colour_from_prefix(
    sku_prefix: str,
    table_name: str | None = None,
) -> str:
    """Get a colour name/value from a SKU prefix."""
    return get_value_from_grouped_yaml(
        config_filepath="config/data/validation/colour_prefixes.yml",
        lookup_key=sku_prefix,
        group_name=table_name,
        group_suffix="_colours",
    )