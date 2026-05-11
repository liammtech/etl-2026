import tools.sql as sql
from tools.config_tools.config_loader import get_colour_from_prefix, get_material_via_range_colour, get_material_via_dimension, get_config_constant_value
import tools.calculations.waterford_qty_per_calcs as waterford

# Global constants

LEGAL_HEIGHTS = [283, 355, 450, 490, 570, 645, 715, 895, 980, 1245]
STANDARD_WIDTHS = [292, 296, 304, 346, 352, 364, 396, 446, 496, 596, 696, 796, 896, 996]
WIDTH_LOWER_BOUND = 196
WIDTH_UPPER_BOUND = 996
SHOULDER_WIDTH = 65

def populate_waterford_m2ms() -> None:

    # 1. Check the system for any live Waterford M2Ms

    current_m2ms = sql.get_multiple_records(
        table="WipMaster",
        criteria={
            "StockCode": "WFD???-ADHOC",
            "Complete": "N" # Validates that job is still in WIP
        },
        return_columns=[
            "Job",
            "JobDescription",
            "StockCode",
            "Complete",
            "QtyToMake",
            "SalesOrderLine"
        ]
    )


    for wip_line in current_m2ms:
        job, sales_order, stock_code, qty_to_make, sales_order_line = [
            wip_line.Job, 
            wip_line.JobDescription, 
            wip_line.StockCode, 
            wip_line.QtyToMake,
            wip_line.SalesOrderLine
        ]

        # Validate that the order is live

        sor_status = sql.get_single_record(
            table="SorMaster",
            criteria={
                "SalesOrder": sales_order
            },
            return_columns={
                "OrderStatus"
            }
        )

        sor_status = sor_status.OrderStatus

        if sor_status == "8" or sor_status == "9":
            print(f"Sales order {sales_order} complete: skipping job {job}...")
            continue

        # Validate that Operations have already been populated
        # TODO: will create a more rigorous validation process at some point
        # Will proceed with basic check now, as Ops are populated on ADHOC codes

        job_ops = sql.get_multiple_records(
            table="WipJobAllLab",
            criteria={
                "Job": job
            },
            order_by="Job"
        )

        if not job_ops:
            # TODO: add in operation loader if no operations found
            print(f"Warning: No operations for job {job}\n" \
                  "Please review. Proceeding to populate materials...")
            
        # Validate that Materials have not already been populated

        job_mats = sql.get_multiple_records(
            table="WipJobAllMat",
            criteria={
                "Job": job
            }
        )

        if job_mats:
            # TODO: add in more robust checker to see if the materials are actually correct
            print(f"Materials found for job {job}\n" \
                  "Review is advised. Skipping...")
            return
        
        '''
        - Get pre-requisite information:
            - Job number x
            - Stock code x
            - Qty to make x
            - Height (CusSorDetailMerch)
            - Width (CusSorDetailMerch)
            - Colour (Derive from stock code)
        '''

        # Get Height + Width from CusSorDetailMerch

        door_dims = sql.get_single_record(
            table="[CusSorDetailMerch+]",
            criteria={
                "SalesOrder": sales_order,
                "SalesOrderInitLine": sales_order_line
            },
            return_columns=[
                "Height",
                "Width"
            ]
        )

        door_height, door_width = [door_dims.Height, door_dims.Width]

        # Determine colour

        sku_prefix = stock_code[:6]

        door_colour = get_colour_from_prefix(sku_prefix=sku_prefix)

        # Validate that height is one of the valid height brackets:

        if door_height not in LEGAL_HEIGHTS:
            print(f"Invalid door height {door_height} for job {job}" \
            "Please review. Skipping...")
            continue

        standard_width_flag = False

        # Check if width is within legal bounds

        if door_width < WIDTH_LOWER_BOUND:
            print(f"Job {job}: width too small @ {door_width} - skipping...")
            continue
        elif door_width > WIDTH_UPPER_BOUND:
            print(f"Job {job}: width too small @ {door_height} - skipping...")
            continue

        # Check whether width is one of standard widths, or if it is a bespoke width

        if door_width in STANDARD_WIDTHS:
            standard_width_flag = True

        # Determine components
        # - - -
        # Centre ZLAM
        centre_panel_zlam = get_material_via_range_colour(
            range="waterford",
            material="centre_panel_zlam",
            colour=door_colour
        )

        zlam_dims = sql.get_single_record(
            table="zInvExtra",
            criteria={
                "StockCode": centre_panel_zlam
            },
            return_columns={
                "Height",
                "Width"
            }
        )

        zlam_height, zlam_width = [zlam_dims.Height, zlam_dims.Width]

        # Height stile

        height_stile_suffix = get_material_via_dimension(
            range="waterford",
            material="height_stile_suffix",
            dimension=str(int(door_height))
        )

        height_stile = sku_prefix + height_stile_suffix

        # Width rail

        width_rail_suffix = None

        if standard_width_flag:
            width_rail_suffix = get_material_via_dimension(
                range="waterford",
                material="height_stile_suffix",
                dimension=str(int(door_height))
            )
        else:
            width_rail_suffix = get_config_constant_value(
                config_filepath="config/materials/waterford_materials.yml",
                lookup_key="m2m_rail_suffix"
            )

        width_rail = sku_prefix + width_rail_suffix

        # Hotfoil

        hotfoil = None

        if not standard_width_flag:
            hotfoil = get_material_via_range_colour(
                range="waterford",
                material="hotfoil",
                colour=door_colour
            )

        # Dowel & glues

        # MS113
        dowel = get_config_constant_value(
            config_filepath="config/materials/waterford_materials.yml",
            lookup_key="dowel"
        )

        # GL085
        dowel_glue = get_config_constant_value(
            config_filepath="config/materials/waterford_materials.yml",
            lookup_key="dowel_glue"            
        )

        # GL105
        silicon = get_config_constant_value(
            config_filepath="config/materials/waterford_materials.yml",
            lookup_key="silicon"            
        )

        # Label
        label = get_config_constant_value(
            config_filepath="config/materials/packaging_materials.yml",
            lookup_key="standard_dn_label"            
        )

        ### QTY PERS
        # TODO: Migrate all to Waterford calcs
        # TODO: Provide a formal interface for "settings" on qty pers

        height_rail_qty = 2     # PCS
        width_rail_qty = None

        if not standard_width_flag:
            width_rail_qty = 2      # PCS
        else:
            m2m_rail_width =  (door_width - (SHOULDER_WIDTH * 2))
            width_rail_qty = waterford.calculate_cut_rail_qty(
                finished_rail_width=m2m_rail_width
            )

        dowel_qty = 8           # PCS
        dowel_glue_qty = 0.002  # KG (GL085)
        silicon = 0.00108       # KG (GL105)
        label = 1               # PCS

        hotfoil_qty = None

        if hotfoil:
            hotfoil_qty = 0.005015 # ROL - this may warrant a review

        centre_panel_qty = waterford.calculate_centre_panel_board_qty(
            door_height=door_height,
            door_width=door_width,
            board_height=zlam_height,
            board_width=zlam_width
        )

        # TODO: DISCOVERY: IT WILL HAVE TO PUT THE OPS IN, SINCE THERE IS NO WAY TO
        # DELINEATE BETWEEN A STANDARD WIDTH AND BESPOKE WIDTH AT SALES ORDER ENTRY
        # AS IT TURNS OUT, THE ROUTINGS FOR EITHER OR ARE NOT THE SAME

        # Op lines