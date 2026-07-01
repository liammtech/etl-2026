import db.sql as sql
from utils.data import reduce_code_to_prefix


def determine_linked_door_component(
    stock_code: str
) -> str:
    
    code_prefix = reduce_code_to_prefix(stock_code=stock_code)

    search_term = code_prefix + "###"
    
    sc_door_height, sc_door_width = sql.get_single_record(
        table="zInvExtra",
        criteria={
            "StockCode": stock_code
        },
        return_columns=["Height", "Width"]
    )

    linked_sku = sql.get_single_record(
        table="zInvExtra",
        criteria={
            "StockCode": search_term,
            "Height": sc_door_height,
            "Width": sc_door_width
        },
        return_columns=["StockCode"],
        flatten=True
    )

    if not linked_sku:
        raise ValueError(f"No linked item found for code {stock_code}")
    else:
        print(f"\nLinked item for {stock_code} found: {linked_sku}")
    
    return linked_sku