from typing import Any, Dict
from tools.config_tools.config_loader import load_row_defaults_wip
from datetime import datetime as Date

def build_single_wipjoballlab_row(
    *,
    job: str,
    operation: int,
    planned_queue_date: Date,
    planned_start_date: Date,
    planned_end_date: Date,
    work_centre: str,
    work_centre_desc: str,
    milestone: str,
    queue_time: int,
    priority: int,
    production_yr_wk: str,
    overlays: Dict[str, Any] = None
) -> Dict[str, Any]:
    row = load_row_defaults_wip(table_name="WipJobAllLab")

    row["Job"] = job
    row["Operation"] = operation
    row["PlannedQueueDate"] = planned_queue_date
    row["PlannedStartDate"] = planned_start_date
    row["PlannedEndDate"] = planned_end_date
    row["WorkCentre"] = work_centre
    row["WorkCentreDesc"] = work_centre_desc
    row["Milestone"] = milestone
    row["QueueTime"] = queue_time
    row["Priority"] = priority
    row["ProductionYrWk"] = production_yr_wk

    if overlays:
        for col, val in overlays.items():
            row[col] = val

    return row
    pass


def build_single_wipjoballmat_row(
    *,
    job: str,
    stock_code: str,
    warehouse: str,
    line: str = "00",
    stock_description: str,
    unit_qty_reqd: float,
    unit_cost: float,
    uom: str,
    bin: str,
    sequence_num: str,
    bulk_issue_item: str = "N",
    scrap_percentage: float,
    kit_issue: str,
    net_unit_qty_reqd: str,
    conv_fact_uom: str,
    unit_qty_reqd_ent: str,
    net_unit_qty_reqd_ent: str,
    overlays: Dict[str, Any] = None
) -> Dict[str, Any]:
    row = load_row_defaults_wip(table_name="WipJobAllMat")

    row["Job"] = job
    row["StockCode"] = stock_code
    row["Warehouse"] = warehouse
    row["Line"] = line
    row["StockDescription"] = stock_description
    row["UnitQtyReqd"] = unit_qty_reqd
    row["UnitCost"] = unit_cost
    row["Uom"] = uom
    row["Bin"] = bin
    row["SequenceNum"] = sequence_num
    row["BulkIssueItem"] = bulk_issue_item
    row["ScrapPercentage"] = scrap_percentage
    row["KitIssue"] = kit_issue
    row["NetUnitQtyReqd"] = net_unit_qty_reqd
    row["ConvFactUom"] = conv_fact_uom
    row["UnitQtyReqdEnt"] = unit_qty_reqd_ent
    row["NetUnitQtyReqdEnt"] = net_unit_qty_reqd_ent

    if overlays:
        for col, val in overlays.items():
            row[col] = val

    return row
    pass