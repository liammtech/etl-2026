from config.loaders.yaml_loader import load_yaml_section


def load_row_defaults(table_name: str) -> dict:
    """Load default row values for a Syspro table."""
    normalised_name = (
        table_name.lower()
        .replace("+", "plus")
        .replace("[", "")
        .replace("]", "")
    )

    return load_yaml_section(
        config_filepath=f"config/defaults/{normalised_name}_defaults.yml",
        section_name=f"{normalised_name}_defaults",
    )