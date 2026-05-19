import sys

from workflows.sku_workflows.reset_mrp_fields import reset_mrp, reset_mrp_range
from workflows.sku_workflows.fix_volumetrics import fix_door_volumetrics, fix_door_volumetrics_range
from workflows.wip_workflows.waterford_m2m import populate_waterford_m2ms
from workflows.bom_workflows.fix_quantities import memp_std_single, lldr_std_single, jayl_std_single
from workflows.bom_workflows.fix_quantities_multiple import memp_std_range, lldr_std_range, jayl_std_range
from workflows.bom_workflows.stocked_to_mto_jpull import switch_jpull_stocked_to_mto
from tools.sku_tools.create_records import create_invwarehouse_record, create_invmasterplus_record


JOBS = {
    # SKU tools
    "jpull-stock-to-mto": switch_jpull_stocked_to_mto,
    "reset-mrp": reset_mrp,
    "reset-mrp-range": reset_mrp_range,
    "fix-door-volumetrics": fix_door_volumetrics,
    "fix-door-volumetrics-range": fix_door_volumetrics_range,

    # WIP tools    
    "populate-waterford-m2ms": populate_waterford_m2ms,

    # Quantity fixers:
    "pressed-slab-qty-single": memp_std_single,
    "pressed-slab-qty-range": memp_std_range,
    "jpull-qty-single": jayl_std_single,
    "jpull-qty-range": jayl_std_range,
    "edged-slab-qty-single": lldr_std_single,
    "edged-slab-qty-range": lldr_std_range,

    # Record creators:
    "create-invwarehouse-record": create_invwarehouse_record,
    "create-invmasterplus-record": create_invmasterplus_record
}


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: basilisc [job] [args...]")
        return

    job_name = args[0]
    job_args = args[1:]

    job = JOBS.get(job_name)

    if job is None:
        print(f"Unknown job: {job_name}")
        return

    job(*job_args)


if __name__ == "__main__":
    main()