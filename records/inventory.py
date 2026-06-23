from typing import Any
from records.builder import build_row

# -- Stock Codes --

def build_invmaster_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="InvMaster",
        values=values,
        overlays=overlays,
    )


def build_invmasterplus_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="[InvMaster+]",
        values=values,
        overlays=overlays,
    )


def build_zinvextra_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="zInvExtra",
        values=values,
        overlays=overlays,
    )


def build_invwarehouse_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="InvWarehouse",
        values=values,
        overlays=overlays,
    )


def build_invwarehouseplus_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="[InvWarehouse+]",
        values=values,
        overlays=overlays,
    )


def build_arcuststkxref_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="ArCustStkXref",
        values=values,
        overlays=overlays,
    )


def build_invnarration_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="InvNarration",
        values=values,
        overlays=overlays,
    )


def build_invnarrationhdr_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="InvNarrationHdr",
        values=values,
        overlays=overlays,
    )


def build_admmultimedia_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="AdmMultimedia",
        values=values,
        overlays=overlays,
    )

# -- Pricing -- 

def build_invprice_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="InvPrice",
        values=values,
        overlays=overlays,
    )

def build_sorcontractprice_row(
    values: dict[str, Any],
    overlays: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_row(
        table_name="SorContractPrice",
        values=values,
        overlays=overlays,
    )
