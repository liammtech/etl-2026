import db.sql as sql
import tools.sku_tools.sku_organisation as sku
import tools.warehouse_tools.warehouse_organisation as warehouse
from config.loaders.yaml_loader import get_config_constant_value
from config.loaders.colours import get_colour_from_prefix
from config.loaders.materials import get_material_via_range_colour, get_material_via_dimension
from tools.row_builders import build_wipjoballlab_row, build_wipjoballmat_row
from tools.work_centre_tools.work_centre_organisation import get_work_centre_description
import domain.manufacturing.qty_per.waterford_qty_per_calcs as waterford
from tools.wip_tools.wip_organisation import get_uom_fields
from datetime import date, timedelta
from decimal import Decimal
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

        print(f"\n\n ROUTE IS {route} \n\n ROUTE DATA TYPE IS {type(route)}\n\n")

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

        # pprint(f"HERE ARE THE JOBS {job_ops}")

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

        # Check if width is within legal bounds

        if door_width < WIDTH_LOWER_BOUND:
            print(f"Job {job}: width too small @ {door_width} - skipping...")
            continue
        elif door_width > WIDTH_UPPER_BOUND:
            print(f"Job {job}: width too small @ {door_height} - skipping...")
            continue

        # Check whether width is one of standard widths, or if it is a bespoke width

        standard_width_flag = False

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

        # print(f"Centre panel ZLAM is {centre_panel_zlam}")

        zlam_height, zlam_width = [zlam_dims.Height, zlam_dims.Width]

        centre_panel_zlam_data = sql.get_single_record(
            table="InvMaster",
            criteria={
                "StockCode": centre_panel_zlam
            }
        )

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
                material="standard_width_rail_suffix",
                dimension=str(int(door_width))
            )
        else:
            width_rail_suffix = get_config_constant_value(
                config_filepath="config/materials/waterford_materials.yml",
                lookup_key="m2m_rail_suffix"
            )

        width_rail = sku_prefix + width_rail_suffix

        width_rail_data = sql.get_single_record(
            table="InvMaster",
            criteria={
                "StockCode": width_rail
            }
        )

        # Hotfoil

        hotfoil = get_material_via_range_colour(
            range="waterford",
            material="hotfoil",
            colour=door_colour
        )

        hotfoil_data = sql.get_single_record(
            table="InvMaster",
            criteria={
                "StockCode": hotfoil
            }
        )

        # Dowel & glues

        # MS113
        dowel = get_config_constant_value(
            config_filepath="config/materials/waterford_materials.yml",
            lookup_key="dowel"
        )

        dowel_data = sql.get_single_record(
            table="InvMaster",
            criteria={
                "StockCode": dowel
            }
        )

        # GL085
        dowel_glue = get_config_constant_value(
            config_filepath="config/materials/waterford_materials.yml",
            lookup_key="dowel_glue"            
        )

        dowel_glue_data = sql.get_single_record(
            table="InvMaster",
            criteria={
                "StockCode": dowel_glue
            }
        )

        # GL105
        silicon = get_config_constant_value(
            config_filepath="config/materials/waterford_materials.yml",
            lookup_key="silicon"            
        )

        silicon_data = sql.get_single_record(
            table="InvMaster",
            criteria={
                "StockCode": silicon
            }
        )

        # Label
        label = get_config_constant_value(
            config_filepath="config/materials/packaging_materials.yml",
            lookup_key="standard_dn_label"            
        )

        label_data = sql.get_single_record(
            table="InvMaster",
            criteria={
                "StockCode": label
            }
        )

        ### QTY PERS
        # TODO: Migrate all to Waterford calcs
        # TODO: Provide a formal interface for "settings" on qty pers

        height_stile_qty = 2     # PCS
        width_rail_qty = None

        if standard_width_flag:
            width_rail_qty = 2      # PCS
        else:
            m2m_rail_width =  (door_width - (SHOULDER_WIDTH * 2))
            width_rail_qty = waterford.calculate_cut_rail_qty(
                finished_rail_width=m2m_rail_width
            )

        dowel_qty = Decimal("0.0152")                           # PCS
        hotfoil_qty = Decimal("0.005015")       # ROL - this may warrant a review
        silicon_qty = Decimal("0.00108")        # KG (GL105)
        label_qty = 1                           # PCS

        dowel_glue_qty = None                   # KG (GL085)

        if standard_width_flag:
            dowel_glue_qty = Decimal("0.002")
        else:
            dowel_glue_qty = Decimal("0.004")

        centre_panel_qty = waterford.calculate_centre_panel_board_qty(
            door_height=door_height,
            door_width=door_width,
            board_height=zlam_height,
            board_width=zlam_width
        )



        # -------------------- OPERATIONS ------------------------------

        job_year = job_delivery_date.strftime("%y")
        job_week = job_delivery_date.isocalendar().week

        production_yr_wk = f"{job_year}/{job_week}"

        # print(f"Job year is {job_year}")
        # print(f"Job week is {job_week}")
        # print(f"Put em together: {job_year}/{job_week}")
        
        # print(f"Job: {job} - Delivery date: {job_delivery_date} - Delivery date type: {type(job_delivery_date)}")

        wip_op_lines = []

        if standard_width_flag and route != "6 ":
            dsjig2_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 1,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
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

            du2rec_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 2,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DU2REC",
                    "WorkCentreDesc": get_work_centre_description("DU2REC"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": 0,
                    "ProductionYrWk": ""
                }
            )

            dppick_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 3,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPPICK",
                    "WorkCentreDesc": get_work_centre_description("DPPICK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dpchk_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 4,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPCHK",
                    "WorkCentreDesc": get_work_centre_description("DPCHK"),
                    "Milestone": "N",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dppack_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 5,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPPACK",
                    "WorkCentreDesc": get_work_centre_description("DPPACK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dpdesp_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 6,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPDESP",
                    "WorkCentreDesc": get_work_centre_description("DPDESP"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            wip_op_lines = [dsjig2_op_line, du2rec_op_line, dppick_op_line, dpchk_op_line, dppack_op_line, dpdesp_op_line]

        elif standard_width_flag and route == "6 ":
            dsjig2_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 1,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
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

            du2rec_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 2,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DU2REC",
                    "WorkCentreDesc": get_work_centre_description("DU2REC"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dppick_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 3,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPPICK",
                    "WorkCentreDesc": get_work_centre_description("DPPICK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dpchk_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 4,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPCHK",
                    "WorkCentreDesc": get_work_centre_description("DPCHK"),
                    "Milestone": "N",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dpdrl_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 5,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPDRL",
                    "WorkCentreDesc": get_work_centre_description("DPDRL"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dppack_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 6,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPPACK",
                    "WorkCentreDesc": get_work_centre_description("DPPACK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dpdesp_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 7,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPDESP",
                    "WorkCentreDesc": get_work_centre_description("DPDESP"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            wip_op_lines = [dsjig2_op_line, du2rec_op_line, dppick_op_line, dpchk_op_line, dpdrl_op_line, dppack_op_line, dpdesp_op_line]

        elif not standard_width_flag and route != "6 ":
            # <--- Start M2M width ops --->
            dgreco_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 1,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
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

            dhfdet_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 2,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
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

            dsprin_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 3,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
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

            dsjig2_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 4,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
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

            du2rec_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 5,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DU2REC",
                    "WorkCentreDesc": get_work_centre_description("DU2REC"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dppick_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 6,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPPICK",
                    "WorkCentreDesc": get_work_centre_description("DPPICK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dpchk_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 7,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPCHK",
                    "WorkCentreDesc": get_work_centre_description("DPCHK"),
                    "Milestone": "N",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dppack_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 8,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPPACK",
                    "WorkCentreDesc": get_work_centre_description("DPPACK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dpdesp_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 9,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPDESP",
                    "WorkCentreDesc": get_work_centre_description("DPDESP"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            wip_op_lines = [dgreco_op_line, dhfdet_op_line, dsprin_op_line, dsjig2_op_line, du2rec_op_line, dppick_op_line, dpchk_op_line, dppack_op_line, dpdesp_op_line]

        elif not standard_width_flag and route == "6 ":
            # <--- Start M2M width ops --->
            dgreco_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 1,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
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

            dhfdet_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 2,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
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

            dsprin_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 3,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
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

            dsjig2_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 4,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
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

            du2rec_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 5,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DU2REC",
                    "WorkCentreDesc": get_work_centre_description("DU2REC"),
                    "Milestone": "Y",
                    "QueueTime": 1
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dppick_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 6,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPPICK",
                    "WorkCentreDesc": get_work_centre_description("DPPICK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dpchk_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 7,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPCHK",
                    "WorkCentreDesc": get_work_centre_description("DPCHK"),
                    "Milestone": "N",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dpdrl_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 8,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPDRL",
                    "WorkCentreDesc": get_work_centre_description("DPDRL"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dppack_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 9,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPPACK",
                    "WorkCentreDesc": get_work_centre_description("DPPACK"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            dpdesp_op_line = build_wipjoballlab_row(
                values={
                    "Job": job,
                    "Operation": 10,
                    "PlannedQueueDate": job_delivery_date,
                    "PlannedStartDate": job_delivery_date,
                    "PlannedEndDate": job_delivery_date,
                    "ParentQtyPlanned": qty_to_make,
                    "ParentQtyPlanEnt": qty_to_make,
                    "WorkCentre": "DPDESP",
                    "WorkCentreDesc": get_work_centre_description("DPDESP"),
                    "Milestone": "Y",
                    "QueueTime": 0
                },
                overlays={
                    "Priority": None,
                    "ProductionYrWk": ""
                }
            )

            wip_op_lines = [dgreco_op_line, dhfdet_op_line, dsprin_op_line, dsjig2_op_line, du2rec_op_line, dppick_op_line, dpchk_op_line, dpdrl_op_line, dppack_op_line, dpdesp_op_line]

        # -------------------- MATERIALS ------------------------------

        height_stile_mat_line = build_wipjoballmat_row(
            values={
                "Job": job,
                "StockCode": height_stile,
                "Warehouse": "DR",
                "StockDescription": height_stile_data.Description,
                "QtyPer": height_stile_qty,
                "UnitCost": height_stile_data.MaterialCost,
                "OperationOffset": dsjig2_op_line.get("Operation"),
                "Uom": height_stile_data.ManufactureUom,
                "Bin": warehouse.get_default_bin(stock_code=height_stile, warehouse="DR"),
                "SequenceNum": "000010",
                "ScrapPercentage": 0,
                "KitIssueItem": "Y",
                **get_uom_fields(
                    invmaster_row=height_stile_data,
                    uom_flag="M",
                ),
            },
            overlays={
                "Line": "00"
            }
        )

        # pprint(height_stile_mat_line)

        # print(f"\n \n WIDTH RAIL IS {width_rail} \n \n")

        width_rail_op = None
        width_rail_mat_line_1 = None
        width_rail_mat_line_2 = None

        if standard_width_flag:

            width_rail_op = dsjig2_op_line.get("Operation")

            width_rail_mat_line_1 = build_wipjoballmat_row(
                values={
                    "Job": job,
                    "StockCode": width_rail,
                    "Warehouse": "DR",
                    "StockDescription": width_rail_data.Description,
                    "QtyPer": width_rail_qty,
                    "UnitCost": width_rail_data.MaterialCost,
                    "OperationOffset": width_rail_op,
                    "Uom": width_rail_data.ManufactureUom,
                    "Bin": warehouse.get_default_bin(stock_code=width_rail, warehouse="DR"),
                    "SequenceNum": "000020",
                    "ScrapPercentage": 0,
                    "KitIssueItem": "Y",
                    **get_uom_fields(
                        invmaster_row=width_rail_data,
                        uom_flag="M"
                    ),
                },
                overlays={
                    "Line": "00"
                }
            )
            # print("HITS NUMBER ONE")

        else:

            width_rail_op = dgreco_op_line.get("Operation")

            width_rail_mat_line_1 = build_wipjoballmat_row(
                values={
                    "Job": job,
                    "StockCode": width_rail,
                    "Warehouse": "DR",
                    "StockDescription": width_rail_data.Description,
                    "QtyPer": width_rail_qty,
                    "UnitCost": width_rail_data.MaterialCost,
                    "OperationOffset": width_rail_op,
                    "Uom": width_rail_data.ManufactureUom,
                    "Bin": warehouse.get_default_bin(stock_code=width_rail, warehouse="DR"),
                    "SequenceNum": "000020",
                    "ScrapPercentage": 0,
                    "KitIssueItem": "Y",
                    **get_uom_fields(
                        invmaster_row=width_rail_data,
                        uom_flag="M"
                    )
                },
                overlays={
                    "Line": "00"
                }
            )

            width_rail_mat_line_2 = build_wipjoballmat_row(
                values={
                    "Job": job,
                    "StockCode": width_rail,
                    "Warehouse": "DR",
                    "StockDescription": width_rail_data.Description,
                    "QtyPer": width_rail_qty,
                    "UnitCost": width_rail_data.MaterialCost,
                    "OperationOffset": width_rail_op,
                    "Uom": width_rail_data.ManufactureUom,
                    "Bin": warehouse.get_default_bin(stock_code=width_rail, warehouse="DR"),
                    "SequenceNum": "000030",
                    "ScrapPercentage": 0,
                    "KitIssueItem": "Y",
                    **get_uom_fields(
                        invmaster_row=width_rail_data,
                        uom_flag="M"
                    )
                },
                overlays={
                    "Line": "01"
                }
            )
            print("HITS NUMBER TWO")

        # pprint(width_rail_mat_line)

        zlam_mat_line = build_wipjoballmat_row(
            values={
                "Job": job,
                "StockCode": centre_panel_zlam,
                "Warehouse": centre_panel_zlam_data.WarehouseToUse,
                "StockDescription": centre_panel_zlam_data.Description,
                "QtyPer": centre_panel_qty,
                "UnitCost": centre_panel_zlam_data.MaterialCost,
                "OperationOffset": dsjig2_op_line.get("Operation"),
                "Uom": centre_panel_zlam_data.ManufactureUom,
                "Bin": warehouse.get_default_bin(stock_code=centre_panel_zlam, warehouse="DW"),
                "SequenceNum": "000030",
                "ScrapPercentage": 13,
                "KitIssueItem": "Y",
                **get_uom_fields(
                    invmaster_row=centre_panel_zlam_data,
                    uom_flag="S"
                )
            },
            overlays={
                "Line": "00"
            }
        )

        # pprint(zlam_mat_line)

        dowel_glue_op = None
        if standard_width_flag:
            dowel_glue_op = dsjig2_op_line.get("Operation")
        else:
            dowel_glue_op = dhfdet_op_line.get("Operation")

        dowel_glue_mat_line = build_wipjoballmat_row(
            values={
                "Job": job,
                "StockCode": dowel_glue,
                "Warehouse": "DR",
                "StockDescription": dowel_glue_data.Description,
                "QtyPer": dowel_glue_qty,
                "UnitCost": dowel_glue_data.MaterialCost,
                "OperationOffset": dowel_glue_op,
                "Uom": dowel_glue_data.ManufactureUom,
                "Bin": warehouse.get_default_bin(stock_code=dowel_glue, warehouse="DR"),
                "SequenceNum": "000040",
                "ScrapPercentage": 0,
                "KitIssueItem": "Y",
                **get_uom_fields(
                    invmaster_row=dowel_glue_data,
                    uom_flag="S"
                )
            },
            overlays={
                "Line": "00"
            }
        )

        silicon_mat_line = build_wipjoballmat_row(
            values={
                "Job": job,
                "StockCode": silicon,
                "Warehouse": "DR",
                "StockDescription": silicon_data.Description,
                "QtyPer": silicon_qty,
                "UnitCost": silicon_data.MaterialCost,
                "OperationOffset": dsjig2_op_line.get("Operation"),
                "Uom": silicon_data.ManufactureUom,
                "Bin": warehouse.get_default_bin(stock_code=silicon, warehouse="DR"),
                "SequenceNum": "000050",
                "ScrapPercentage": 10,
                "KitIssueItem": "Y",
                **get_uom_fields(
                    invmaster_row=silicon_data,
                    uom_flag="S"
                )
            },
            overlays={
                "Line": "00"
            }
        )

        label_mat_line = build_wipjoballmat_row(
            values={
                "Job": job,
                "StockCode": label,
                "Warehouse": "DR",
                "StockDescription": label_data.Description,
                "QtyPer": label_qty,
                "UnitCost": label_data.MaterialCost,
                "OperationOffset": dsjig2_op_line.get("Operation"),
                "Uom": label_data.ManufactureUom,
                "Bin": warehouse.get_default_bin(stock_code=label, warehouse="DR"),
                "SequenceNum": "000060",
                "ScrapPercentage": 0,
                "KitIssueItem": "N",
                **get_uom_fields(
                    invmaster_row=label_data,
                    uom_flag="S"
                )
            },
            overlays={
                "Line": "00"
            }
        )
        # pprint(silicon_mat_line)

        wip_material_lines = [
            height_stile_mat_line,
            width_rail_mat_line_1,
            zlam_mat_line,
            dowel_glue_mat_line,
            silicon_mat_line,
            label_mat_line
        ]

        hotfoil_mat_line = None
        dowel_mat_line = None

        if not standard_width_flag:

            hotfoil_mat_line = build_wipjoballmat_row(
                values={
                    "Job": job,
                    "StockCode": hotfoil,
                    "Warehouse": "DR",
                    "StockDescription": hotfoil_data.Description,
                    "QtyPer": hotfoil_qty,
                    "UnitCost": hotfoil_data.MaterialCost,
                    "OperationOffset": dsjig2_op_line.get("Operation"),
                    "Uom": hotfoil_data.ManufactureUom,
                    "Bin": warehouse.get_default_bin(stock_code=hotfoil, warehouse="DR"),
                    "SequenceNum": "000070",
                    "ScrapPercentage": 0,
                    "KitIssueItem": "N",
                    **get_uom_fields(
                        invmaster_row=hotfoil_data,
                        uom_flag="M"
                    )
                },
                overlays={
                    "Line": "00"
                }
            )

            dowel_mat_line = build_wipjoballmat_row(
                values={
                    "Job": job,
                    "StockCode": dowel,
                    "Warehouse": "DR",
                    "StockDescription": dowel_data.Description,
                    "QtyPer": dowel_qty,
                    "UnitCost": dowel_data.MaterialCost,
                    "OperationOffset": dsjig2_op_line.get("Operation"),
                    "Uom": dowel_data.ManufactureUom,
                    "Bin": warehouse.get_default_bin(stock_code=dowel, warehouse="DR"),
                    "SequenceNum": "000080",
                    "ScrapPercentage": 0,
                    "KitIssueItem": "N",
                    **get_uom_fields(
                        invmaster_row=dowel_data,
                        uom_flag="S"
                    )
                },
                overlays={
                    "Line": "00"
                }
            )

            wip_material_lines.append(width_rail_mat_line_2)
            wip_material_lines.append(hotfoil_mat_line)
            wip_material_lines.append(dowel_mat_line)

        # pprint(wip_material_lines)
        # pprint(f"Standard width flag for job {job}: {standard_width_flag}")

        # for line in wip_material_lines:
            # print(f"Material for job {job}: {line}")

        for line in wip_op_lines:
            sql.append_single_record(
                table="WipJobAllLab",
                row=line
            )

        for line in wip_material_lines:
            sql.append_single_record(
                table="WipJobAllMat",
                row=line
            )

        pprint(f"Jobs acted on: \n {current_m2ms}")