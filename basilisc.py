import sys, json

from workflows.sku_workflows.reset_mrp_fields import reset_mrp, reset_mrp_range
from workflows.sku_workflows.fix_volumetrics import fix_door_volumetrics, fix_door_volumetrics_range
from workflows.wip_workflows.waterford_m2m import populate_waterford_m2ms
from workflows.bom_workflows.fix_quantities import memp_std_single, lldr_std_single, jayl_std_single
from workflows.bom_workflows.fix_quantities_multiple import memp_std_range, lldr_std_range, jayl_std_range
from workflows.bom_workflows.stocked_to_mto_jpull import switch_jpull_stocked_to_mto, jpull_range_to_mto
from workflows.bom_workflows.restore_linked_stock_codes import restore_linked_sku, restore_linked_skus_range
from workflows.bom_workflows.create_records import create_invwarehouse_record, create_invmasterplus_record, create_invwarehouse_record_range, create_full_sales_code_routings
from workflows.bom_workflows.d_codes import sub_out_d_code
from tools.sku_tools.palletisation import determine_pallet_spec

from dotenv import load_dotenv
import os

load_dotenv()

args_file = os.getenv("BASILISC_ARGS_FILE")

JOBS = {
    # SKU tools
    "jpull-stock-to-mto": switch_jpull_stocked_to_mto,
    "jpull-range-to-mto": jpull_range_to_mto,
    "restore-linked-sku": restore_linked_sku,
    "restore-linked-skus-range": restore_linked_skus_range,
    "reset-mrp": reset_mrp,
    "reset-mrp-range": reset_mrp_range,
    "fix-door-volumetrics": fix_door_volumetrics,
    "fix-door-volumetrics-range": fix_door_volumetrics_range,
    "determine-pallet-spec": determine_pallet_spec,

    # BOM tools
    "create-full-sales-code-routings": create_full_sales_code_routings,
    "sub-out-d-code": sub_out_d_code,

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
    "create-invmasterplus-record": create_invmasterplus_record,
    "create-invwarehouse-record-range": create_invwarehouse_record_range
}

def parse_cli_arg(arg: str):
    arg = arg.strip()

    # Only attempt JSON parsing for JSON-looking values
    if not (
        arg.startswith("{")
        or arg.startswith("[")
        or arg.startswith('"')
    ):
        return arg

    try:
        return json.loads(arg)
    except json.JSONDecodeError:
        return arg

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

    parsed_job_args = [parse_cli_arg(arg) for arg in job_args]

    print(sys.argv)
    print(job_args)

    job(*parsed_job_args)


if __name__ == "__main__":
    main()