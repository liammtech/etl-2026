from dataclasses import dataclass
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/arcuststkxref_defaults.yml

@dataclass
class ArCustStkXrefRow:
    Customer: str
    CustStockCode: str
    StockCode: str
    Description: Optional[str]
    LongDesc: Optional[str]