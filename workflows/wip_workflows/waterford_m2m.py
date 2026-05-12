import tools.sql as sql
import tools.sku_tools.sku_organisation as sku
import tools.warehouse_tools.warehouse_organisation as warehouse
from tools.config_tools.config_loader import get_colour_from_prefix, get_material_via_range_colour, get_material_via_dimension, get_config_constant_value
from tools.row_builders import build_wipjoballlab_row, build_wipjoballmat_row
from tools.work_centre_tools.work_centre_organisation import get_work_centre_description
import tools.calculations.waterford_qty_per_calcs as waterford
from tools.wip_tools.wip_organisation import get_uom_conversion_fields
from datetime import date, timedelta
from pprint import pprint


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
            "JobDeliveryDate",
            "Complete",
            "QtyToMake",
            "Route",
            "SalesOrderLine"
        ]
    )

    for wip_line in current_m2ms:
        job, sales_order, stock_code, job_delivery_date, qty_to_make, route, sales_order_line = [
            wip_line.Job, 
            wip_line.JobDescription, 
            wip_line.StockCode,
            wip_line.JobDeliveryDate,
            wip_line.QtyToMake,
            wip_line.Route,
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

        # Validate that Operations have not already been populated
        # TODO: Discovered that we need to put the ops in at every turn

        job_ops = sql.get_multiple_records(
            table="WipJobAllLab",
            criteria={
                "Job": job
            },
            order_by="Job"
        )

        pprint(f"HERE ARE THE JOBS {job_ops}")

        if job_ops:
            # TODO: add in operation loader if no operations found
            print(f"Warning: Operations for job {job}\n" \
                  "Review is advised. Skipping...")
            continue
            
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
            continue
        
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

        print(f"Centre panel ZLAM is {centre_panel_zlam}")

        zlam_height, zlam_width = [zlam_dims.Height, zlam_dims.Width]

        # Height stile

        height_stile_suffix = get_material_via_dimension(
            range="waterford",
            material="height_stile_suffix",
            dimension=str(int(door_height))
        )

        height_stile = sku_prefix + height_stile_suffix

        height_stile_data = sql.get_single_record(
            table="InvMaster",
            criteria={
                "StockCode": height_stile
            }
        )

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

        height_stile_qty = 2     # PCS
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

        # -------------------- OPERATIONS ------------------------------

        job_year = job_delivery_date.strftime("%y")
        job_week = job_delivery_date.isocalendar().week

        production_yr_wk = f"{job_year}/{job_week}"

        print(f"Job year is {job_year}")
        print(f"Job week is {job_week}")
        print(f"Put em together: {job_year}/{job_week}")
        
        print(f"Job: {job} - Delivery date: {job_delivery_date} - Delivery date type: {type(job_delivery_date)}")

        wip_ops = []

        if standard_width_flag and route != "6":
            dsjig2_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 1,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DSJIG2",
                    "WorkCentreDesc": get_work_centre_description("DSJIG2"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 9999,
                    "ProductionYrWk": production_yr_wk
                }
            )

            du2rec_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 2,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DU2REC",
                    "WorkCentreDesc": get_work_centre_description("DU2REC"),
                    "Milestone": "Y",
                    "QueueTime": 1
                }
            )

            dppick_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 3,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPPICK",
                    "WorkCentreDesc": get_work_centre_description("DPPICK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            dpchk_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 4,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPCHK",
                    "WorkCentreDesc": get_work_centre_description("DPCHK"),
                    "Milestone": "N",
                    "QueueTime": 0
                }
            )

            dppack_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 5,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPPACK",
                    "WorkCentreDesc": get_work_centre_description("DPPACK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            dpdesp_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 6,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPDESP",
                    "WorkCentreDesc": get_work_centre_description("DPDESP"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            wip_ops = [dsjig2_op, du2rec_op, dppick_op, dpchk_op, dppack_op, dpdesp_op]

        elif standard_width_flag and route == "6":
            dsjig2_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 1,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DSJIG2",
                    "WorkCentreDesc": get_work_centre_description("DSJIG2"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 9999,
                    "ProductionYrWk": production_yr_wk
                }
            )

            du2rec_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 2,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DU2REC",
                    "WorkCentreDesc": get_work_centre_description("DU2REC"),
                    "Milestone": "Y",
                    "QueueTime": 1
                }
            )

            dppick_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 3,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPPICK",
                    "WorkCentreDesc": get_work_centre_description("DPPICK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            dpchk_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 4,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPCHK",
                    "WorkCentreDesc": get_work_centre_description("DPCHK"),
                    "Milestone": "N",
                    "QueueTime": 0
                }
            )

            dpdrl_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 5,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPDRL",
                    "WorkCentreDesc": get_work_centre_description("DPDRL"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            dppack_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 6,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPPACK",
                    "WorkCentreDesc": get_work_centre_description("DPPACK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            dpdesp_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 7,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPDESP",
                    "WorkCentreDesc": get_work_centre_description("DPDESP"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            wip_ops = [dsjig2_op, du2rec_op, dppick_op, dpchk_op, dpdrl_op, dppack_op, dpdesp_op]

        elif not standard_width_flag and route != "6":
            # <--- Start M2M width ops --->
            dgreco_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 1,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DGRECO",
                    "WorkCentreDesc": get_work_centre_description("DGRECO"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 9999,
                    "ProductionYrWk": production_yr_wk
                }
            )

            dhfdet_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 2,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DHFDET",
                    "WorkCentreDesc": get_work_centre_description("DHFDET"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 9999,
                    "ProductionYrWk": production_yr_wk
                }
            )

            dsprin_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 3,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DSPRIN",
                    "WorkCentreDesc": get_work_centre_description("DSPRIN"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 9999,
                    "ProductionYrWk": production_yr_wk
                }
            )

            # <--- Stop M2M width ops --->

            dsjig2_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 4,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DSJIG2",
                    "WorkCentreDesc": get_work_centre_description("DSJIG2"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 9999,
                    "ProductionYrWk": f"{job_year}/{job_week}"
                }
            )

            du2rec_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 5,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DU2REC",
                    "WorkCentreDesc": get_work_centre_description("DU2REC"),
                    "Milestone": "Y",
                    "QueueTime": 1
                }
            )

            dppick_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 6,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPPICK",
                    "WorkCentreDesc": get_work_centre_description("DPPICK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            dpchk_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 7,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPCHK",
                    "WorkCentreDesc": get_work_centre_description("DPCHK"),
                    "Milestone": "N",
                    "QueueTime": 0
                }
            )

            dppack_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 8,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPPACK",
                    "WorkCentreDesc": get_work_centre_description("DPPACK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            dpdesp_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 9,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPDESP",
                    "WorkCentreDesc": get_work_centre_description("DPDESP"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            wip_ops = [dgreco_op, dhfdet_op, dsprin_op, dsjig2_op, du2rec_op, dppick_op, dpchk_op, dppack_op, dpdesp_op]

        elif not standard_width_flag and route == "6":
            # <--- Start M2M width ops --->
            dgreco_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 1,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DGRECO",
                    "WorkCentreDesc": get_work_centre_description("DGRECO"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 9999,
                    "ProductionYrWk": production_yr_wk
                }
            )

            dhfdet_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 2,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DHFDET",
                    "WorkCentreDesc": get_work_centre_description("DHFDET"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 9999,
                    "ProductionYrWk": production_yr_wk
                }
            )

            dsprin_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 3,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DSPRIN",
                    "WorkCentreDesc": get_work_centre_description("DSPRIN"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 9999,
                    "ProductionYrWk": production_yr_wk
                }
            )

            # <--- Stop M2M width ops --->

            dsjig2_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 4,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DSJIG2",
                    "WorkCentreDesc": get_work_centre_description("DSJIG2"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 9999,
                    "ProductionYrWk": f"{job_year}/{job_week}"
                }
            )

            du2rec_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 5,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DU2REC",
                    "WorkCentreDesc": get_work_centre_description("DU2REC"),
                    "Milestone": "Y",
                    "QueueTime": 1
                }
            )

            dppick_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 6,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPPICK",
                    "WorkCentreDesc": get_work_centre_description("DPPICK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            dpchk_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 7,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPCHK",
                    "WorkCentreDesc": get_work_centre_description("DPCHK"),
                    "Milestone": "N",
                    "QueueTime": 0
                }
            )

            dpchk_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 8,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPDRL",
                    "WorkCentreDesc": get_work_centre_description("DPDRL"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            dppack_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 9,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPPACK",
                    "WorkCentreDesc": get_work_centre_description("DPPACK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            dpdesp_op = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 10,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "WorkCentre": "DPDESP",
                    "WorkCentreDesc": get_work_centre_description("DPDESP"),
                    "Milestone": "Y",
                    "QueueTime": 0
                }
            )

            wip_ops = [dgreco_op, dhfdet_op, dsprin_op, dsjig2_op, du2rec_op, dppick_op, dpchk_op, dpdrl_op, dppack_op, dpdesp_op]

        # -------------------- MATERIALS ------------------------------

        height_stile_line = build_wipjoballmat_row(
            values={
                "Job": job,
                "StockCode": height_stile,
                "Warehouse": "DW",
                "StockDescription": height_stile_data.Description,
                "QtyPer": height_stile_qty,
                "UnitCost": height_stile_data.MaterialCost,
                "OperationOffset": dsjig2_op.get("Operation"),
                "Uom": height_stile_data.ManufactureUom,
                "Bin": warehouse.get_default_bin(stock_code=height_stile),
                "SequenceNum": "000010",
                "ScrapPercentage": 0,
                "KitIssueItem": "Y",
                **get_uom_conversion_fields(
                    invmaster_row=height_stile_data,
                    uom_flag="M",
                ),
            }
        )