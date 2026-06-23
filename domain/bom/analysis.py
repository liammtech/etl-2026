import db.sql as sql
from collections import Counter

def get_range_modal_component(
    *,
    stock_code_prefix: str,
    component_prefixes: str | list[str]
) -> str:
    all_components = sql.get_multiple_records(
        table="BomStructure",
        criteria={
            "ParentPart": stock_code_prefix,
            "Component": component_prefixes
        },
        return_columns=["Component"]
    )

    all_components = [item for sublist in all_components for item in sublist]
    components_count = Counter(list(all_components))
    modal_component = components_count.most_common()[0][0]

    print(modal_component)
    return modal_component
