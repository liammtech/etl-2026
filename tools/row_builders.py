from typing import Any, Dict
from tools.config_tools.config_loader import load_row_defaults

def build_single_bomoperations_row(
    *,
    stock_code: str,
    route: str = "0",
    operation: int = 1,
    work_centre: str,
    overlays: Dict[str, Any] = None
) -> Dict[str, Any]:
    
    row = load_row_defaults(table_name = "BomOperations")

    row["StockCode"] = stock_code
    row["Route"] = route
    row["Operation"] = operation
    row["WorkCentre"] = work_centre

    if overlays:
        for col, val in overlays.items():
            row[col] = val

    return row

def build_single_bomstructure_row(
    *,
    parent_part: str,
    route: str = "0",
    operation: int = 1,
    component: str,
    overlays: Dict[str, Any] = None
) -> Dict[str, Any]:
    
    row = load_row_defaults(table_name = "BomStructure")

    row["ParentPart"] = parent_part
    row["Route"] = route
    row["OperationOffset"] = operation
    row["Component"] = component

    if overlays:
        for col, val in overlays.items():
            row[col] = val

    return row
