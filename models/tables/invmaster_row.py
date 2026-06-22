from dataclasses import dataclass
from decimal import *
from datetime import date
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/invmaster_defaults.yml

@dataclass
class InvMasterRow:
    StockCode: str
    Description: str
    LongDesc: str
    AlternateKey1: str
    AlternateKey2: str
    ProductClass: str
    StockUom: Optional[str] = None
    AlternateUom: Optional[str] = None
    OtherUom: Optional[str] = None
    ConvFactAltUom: Optional[Decimal] = None
    ConvMulDiv: Optional[str] = None
    ConvFactOthUom: Optional[Decimal] = None
    MulDiv: Optional[str] = None   
    Mass: Optional[Decimal] = None
    Supplier: Optional[Decimal] = None
    ListPriceCode: Optional[str] = None
    Buyer: Optional[str] = None
    Planner: Optional[str] = None
    LeadTime: Optional[Decimal] = None
    SupercessionDate: Optional[date] = None
    MaterialCost: Optional[Decimal] = None
    PartCategory: Optional[str] = None
    DrawOfficeNum: Optional[str] = None
    WarehouseToUse: Optional[str] = None
    BuyingRule: Optional[str] = None
    Ebq: Optional[Decimal] = None
    PanSize: Optional[Decimal] = None
    MakeToOrderFlag: Optional[str] = None
    ManufLeadTime: Optional[Decimal] = None
    UserField1: Optional[str] = None          # Used for pallet spec (and other things)
    UserField2: Optional[Decimal] = None      # Used for profile wrap width
    UserField4: Optional[str] = None          # Supply chain audit flag "K" for handful of codes
    UserField5: Optional[str] = None          # Number of flag options - supply chain audit
    TariffCode: Optional[str] = None          # Need to look up logic to be applied, approx 40 different tariff codes on system
    StockOnHold: Optional[str] = None
    DateStkAdded: Optional[date] = None
    ManufactureUom: Optional[str] = None
    ConvFactMuM: Optional[Decimal] = None
    ManMulDiv: Optional[str] = None