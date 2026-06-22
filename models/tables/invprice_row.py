from dataclasses import dataclass
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/invprice_defaults.yml

@dataclass
class InvPriceRow:
    StockCode: str
    PriceCode: Optional[str]
    SellingPrice: Optional[Decimal]
    