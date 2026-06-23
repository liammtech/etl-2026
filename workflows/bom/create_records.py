import db.sql as sql
from datetime import datetime
import tools.row_builders as row_builder

# These builders act as an interface to the row builders, that actually set up and post the table records in the format that they generally want to exist in on the system

def create_invwarehouse_record(
    stock_code: str,
    warehouse: str = "DW"
) -> None:

    invwarehouse_row = row_builder.build_invwarehouse_row(
        values={
            "StockCode": stock_code,
            "Warehouse": warehouse,
            "DefaultBin": warehouse,
            "DateWhAdded": datetime.now().date()
        }
    )

    sql.append_single_record(
        table="InvWarehouse",
        row=invwarehouse_row
    )


def create_invwarehouse_record_range(stock_code: str):
    
    door_range_result = sql.get_multiple_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code,
        },
        return_columns=[
            "StockCode"
        ]
    )
    
    # door_range = [item for sublist in door_range_result for item in sublist]
    door_range = ["KKHKNCUP64SS","KKHKNDH96SS","KKHKNKNOSS","KKHKNCUP64MB","KKHKNDH96MB","KKHKNKNOMB","KKHKNCUP64AB","KKHKNDH96AB","KKHKNKNOAB","KKHPOLKNOBLN","KKHPOLCUP76BLN","KKHHENKNOPC","KKHHENDH96PC","KKHHENKNOSS","KKHHENDH96SS"]

    for sku in door_range:
        create_invwarehouse_record(stock_code=sku)



def create_invmasterplus_record(
    stock_code: str
) -> None:
    
    invmasterplus_row = row_builder.build_invmasterplus_row(
        values={
            "StockCode": stock_code
        }
    )

    sql.append_single_record(
        table="[InvMaster+]",
        row=invmasterplus_row
    )

def create_invmasterplus_record_range(stock_code: str):
    
    door_range_result = sql.get_multiple_records(
        table="InvMaster",
        criteria={
            "StockCode": stock_code,
        },
        return_columns=[
            "StockCode"
        ]
    )
    
    # door_range = [item for sublist in door_range_result for item in sublist]
    door_range = ["KKHKNCUP64SS","KKHKNDH96SS","KKHKNKNOSS","KKHKNCUP64MB","KKHKNDH96MB","KKHKNKNOMB","KKHKNCUP64AB","KKHKNDH96AB","KKHKNKNOAB","KKHPOLKNOBLN","KKHPOLCUP76BLN","KKHHENKNOPC","KKHHENDH96PC","KKHHENKNOSS","KKHHENDH96SS"]

    for sku in door_range:
        create_invmasterplus_record(stock_code=sku)


def create_arcuststkref_record(
    
) -> None:
    pass


def create_std_sales_code_ops(
    stock_code: str,
    route: str    
) -> None:
    
    dppick_row = row_builder.build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": route,
            "Operation": 1,
            "WorkCentre": "DPPICK",
            "Milestone": "Y"
        }
    )
    
    dpchk_row = row_builder.build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": route,
            "Operation": 2,
            "WorkCentre": "DPCHK",
            "Milestone": "N"
        }
    )
    
    dppack_row = row_builder.build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": route,
            "Operation": 3,
            "WorkCentre": "DPPACK",
            "Milestone": "Y"
        }
    )
    
    dpdesp_row = row_builder.build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": route,
            "Operation": 4,
            "WorkCentre": "DPDESP",
            "Milestone": "Y"
        }
    )

    ops_list = [dppick_row, dpchk_row, dppack_row, dpdesp_row]

    sql.append_multiple_records(
        table="BomOperations",
        rows=ops_list
    )


def create_std_drilled_sales_ops(
    stock_code: str,
    route: str = "6"   
) -> None:
    
    dppick_row = row_builder.build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": route,
            "Operation": 1,
            "WorkCentre": "DPPICK",
            "Milestone": "Y"
        }
    )
    
    dpchk_row = row_builder.build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": route,
            "Operation": 2,
            "WorkCentre": "DPCHK",
            "Milestone": "N"
        }
    )
    
    dpdrl_row = row_builder.build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": route,
            "Operation": 3,
            "WorkCentre": "DPDRL",
            "Milestone": "Y"
        }
    )
    
    dppack_row = row_builder.build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": route,
            "Operation": 4,
            "WorkCentre": "DPPACK",
            "Milestone": "Y"
        }
    )
    
    dpdesp_row = row_builder.build_bomoperations_row(
        values={
            "StockCode": stock_code,
            "Route": route,
            "Operation": 5,
            "WorkCentre": "DPDESP",
            "Milestone": "Y"
        }
    )

    ops_list = [dppick_row, dpchk_row, dpdrl_row, dppack_row, dpdesp_row]

    sql.append_multiple_records(
        table="BomOperations",
        rows=ops_list
    )


def create_std_sales_code_bom(
    parent_part: str,
    component: str,
    route: str = "6",
    skip_label: bool = False 
) -> None:
    
    material_row = row_builder.build_bomstructure_row(
        values={
            "ParentPart": parent_part,
            "Component": component,
            "Route": route,
            "OperationOffset": 1,
            "SequenceNum": "000010",
            "InclKitIssues": "Y"
        }
    )

    if not skip_label:
        label_row = row_builder.build_bomstructure_row(
            values={
                "ParentPart": parent_part,
                "Component": "PK0179",
                "Route": route,
                "OperationOffset": 1,
                "SequenceNum": "000020",
                "InclKitIssues": "N"
            }
        )

    bom_list = [material_row, label_row]

    sql.append_multiple_records(
        table="BomStructure",
        rows=bom_list
    )


# Recursive sales code BOMs - until I can figure out where to put them

def create_full_sales_code_routings(
    parent_child_skus: dict,
    routes: list         
) -> None:
    for parent_sku, child_sku in parent_child_skus.items():
        for r in routes:
            create_std_sales_code_ops(
                stock_code=parent_sku,
                route=r
            )

            create_std_sales_code_bom(
                parent_part=parent_sku,
                component=child_sku,
                route=r
            )
 