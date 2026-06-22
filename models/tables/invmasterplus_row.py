from dataclasses import dataclass
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/invmasterplus_defaults.yml

@dataclass
class InvMasterPlusRow:
    StockCode: str
    SkuStatus: Optional[str] = None
    Planner2: Optional[str] = None
    SupplyLeadTime: Optional[Decimal] = None
    ReplaceLeadTime: Optional[Decimal] = None
    QuoteReference: Optional[str] = None
    BaRangeName: Optional[str] = None
    CustomerRangeName: Optional[str] = None
    RangeMoq: Optional[Decimal] = None
    MinimumOrderQty: Optional[Decimal] = None
    RouteToMarket: Optional[str] = None
    Planner3: Optional[str] = None
    FixedWeight: Optional[Decimal] = None
    Force2ManDelivery: Optional[str] = None
    SupplierDelivers: Optional[str] = None