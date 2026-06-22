from .admmultimedia_row import AdmMultimediaRow
from .arcuststkxref_row import ArCustStkXrefRow
from .bomoperations_row import BomOperationsRow
from .bomoperationsplus_row import BomOperationsPlusRow
from .bomstructure_row import BomStructureRow
from .bomstructureplus_row import BomStructurePlusRow
from .invmaster_row import InvMasterRow
from .invmasterplus_row import InvMasterPlusRow
from .invnarration_row import InvNarrationRow
from .invnarrationhdr_row import InvNarrationHdrRow
from .invprice_row import InvPriceRow
from .invwarehouse_row import InvWarehouseRow
from .invwarehouseplus_row import InvWarehousePlusRow
from .porsupstkinfo_row import PorSupStkInfoRow
from .porsupstkinter_row import PorSupStkInterRow
from .porxrefprices_row import PorXrefPrices
from .sorcontractprice_row import SorContractPrice
from .wipjoballlab_row import WipJobAllLabRow
from .wipjoballmat_row import WipJobAllMatRow
from .zinvextra_row import ZInvExtraRow


MODEL_REGISTRY = {
    "AdmMultimedia": AdmMultimediaRow,
    "ArCustStkXref": ArCustStkXrefRow,
    "BomOperations": BomOperationsRow,
    "BomOperations+": BomOperationsPlusRow,
    "BomStructure": BomStructureRow,
    "BomStructure+": BomStructurePlusRow,
    "InvMaster": InvMasterRow,
    "InvMaster+": InvMasterPlusRow,
    "InvNarration": InvNarrationRow,
    "InvNarrationHdr": InvNarrationHdrRow,
    "InvPrice": InvPriceRow,
    "InvWarehouse": InvWarehouseRow,
    "InvWarehouse+": InvWarehousePlusRow,
    "PorSupStkInfo": PorSupStkInfoRow,
    "PorSupStkInter": PorSupStkInterRow,
    "PorXrefPrices": PorXrefPrices,
    "SorContractPrice": SorContractPrice,
    "WipJobAllLab": WipJobAllLabRow,
    "WipJobAllMat": WipJobAllMatRow,
    "zInvExtra": ZInvExtraRow,
}


__all__ = [
    "AdmMultimediaRow",
    "ArCustStkXrefRow",
    "BomOperationsRow",
    "BomOperationsPlusRow",
    "BomStructureRow",
    "BomStructurePlusRow",
    "InvMasterRow",
    "InvMasterPlusRow",
    "InvNarrationRow",
    "InvNarrationHdrRow",
    "InvPriceRow",
    "InvWarehouseRow",
    "InvWarehousePlusRow",
    "PorSupStkInfoRow",
    "PorSupStkInterRow",
    "PorXrefPrices",
    "SorContractPrice",
    "WipJobAllLabRow",
    "WipJobAllMatRow",
    "ZInvExtraRow",
    "MODEL_REGISTRY",
]