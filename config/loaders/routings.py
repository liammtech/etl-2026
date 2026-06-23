from config.loaders.yaml_loader import load_yaml
from typing import Literal


def get_routings_by_category(
    routing_category: str
) -> str:
    """Get the critical values for a particular type of operations list."""
    return load_yaml(
        config_filepath=f"config/data/routings/{routing_category}.yml"
    )

# Add more loaders, specific to each routing type