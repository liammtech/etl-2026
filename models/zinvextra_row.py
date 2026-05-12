from dataclasses import dataclass
from decimal import *
from datetime import date
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/zinvextra_defaults.yml

@dataclass
class ZInvExtraRow:
    StockCode: str
    Customer: str
    RangeName: str
    LinkedStockCode: str
    DateAdded: date
    AddedUser: str
    DateLastChanged: date
    ChangeUser: str
    DrawingLocation: Optional[str] = None
    DrawingLocation2: Optional[str] = None
    DrawingLocation3: Optional[str] = None
    DrawingLocation4: Optional[str] = None
    DrawingLocation5: Optional[str] = None
    QuoteLocation: Optional[str] = None
    ProductCategory: Optional[str] = None
    ProductType: Optional[str] = None
    InternalProductDescription: Optional[str] = None
    Height: Optional[Decimal] = None
    Width: Optional[Decimal] = None
    Thickness: Optional[Decimal] = None
    ProductStyle: Optional[str] = None
    GrainDirection: Optional[str] = None
    FoilType: Optional[str] = None
    Obsolete: Optional[str] = None
    ProfileSectionWidth: Optional[Decimal] = None
    ProfileSectionThickness: Optional[Decimal] = None
    NumPieces: Optional[Decimal] = None
    Comments: Optional[str] = None
    PalletID: Optional[str] = None
    PalletSpecification: Optional[str] = None
    OptimumPalletSize: Optional[str] = None
    ItemsPerLayer: Optional[Decimal] = None
    StackHeight: Optional[Decimal] = None
    PalletPackSize: Optional[Decimal] = None
    AveragePalletWeight: Optional[Decimal] = None
    PalletLabelLocation: Optional[str] = None
    PalletLabelQty: Optional[str] = None
    CamProgram: Optional[str] = None