from functools import lru_cache
from pathlib import Path

from config.loaders.yaml_loader import load_yaml


ROUTINGS_DIR = Path("config/data/routings")


@lru_cache
def load_all_routing_templates() -> dict[str, list[dict]]:
    """Load all configured routing templates from YAML files."""
    templates = {}

    for filepath in ROUTINGS_DIR.glob("*.yml"):
        data = load_yaml(config_filepath=str(filepath))

        # duplicates = set(data) & set(templates)
        # if duplicates:
        #     raise ValueError(
        #         f"Duplicate routing template names found: {duplicates}"
        #     )

        templates.update(data)

    return templates


def get_routing_template(template_name: str) -> list[dict]:
    """Get a named routing template."""
    templates = load_all_routing_templates()

    if template_name not in templates:
        raise ValueError(f"Unknown routing template: {template_name!r}")

    return templates[template_name]