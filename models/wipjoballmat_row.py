from dataclasses import dataclass
from datetime import date
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/zinvextra_defaults.yml

@dataclass
class WipJobAllMatRow:
    Job: str
    StockCode: str
    Warehouse: str
    StockDescription: str
    UnitQtyReqd: Decimal
    UnitCost: Decimal
    OperationOffset: int
    Uom: str
    Bin: str
    SequenceNum: str
    BulkIssueItem: str
    ScrapPercentage: Decimal
    KitIssueItem: str
    NetUnitQtyReqd: Decimal
    Line: str = "00"