from typing import Literal
from config.loaders.yaml_loader import load_yaml

def get_kitchen_kit_values(
    value_group: Literal[
        "cab-colours",
        "cab-configs",
        "door-colours",
        "door-sizes",
        "door-styles",
        "product-classes",
        "service-types"
    ]
):

    match value_group:
        case "cab-colours":
            return load_yaml(config_filepath="config/data/validation/kitchen_kit/kitchen_kit_cab_colours.yml")
        case "cab-configs":
            return load_yaml(config_filepath="config/data/validation/kitchen_kit/kitchen_kit_cab_configs.yml")
        case "door-colours":
            return load_yaml(config_filepath="config/data/validation/kitchen_kit/kitchen_kit_door_colours.yml")
        case "door-styles":
            return load_yaml(config_filepath="config/data/validation/kitchen_kit/kitchen_kit_door_styles.yml")
        case "door-sizes":
            return load_yaml(config_filepath="config/data/validation/kitchen_kit/kitchen_kit_door_sizes.yml")
        case "product-classes":
            return load_yaml(config_filepath="config/data/validation/kitchen_kit/kitchen_kit_product_classes.yml")
        case "service-types":
            return load_yaml(config_filepath="config/data/validation/kitchen_kit/kitchen_kit_service_types.yml")