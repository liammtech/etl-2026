import db.sql as sql
import records.bom as bom
from domain.bom.templates.routing_templates import create_routing_from_template


def create_std_sales_code_ops(stock_code: str, route: str) -> None:
    create_routing_from_template(
        stock_code=stock_code,
        route=route,
        template_name="standard_sales",
    )


def create_std_drilled_sales_code_ops(stock_code: str, route: str) -> None:
    create_routing_from_template(
        stock_code=stock_code,
        route=route,
        template_name="drilled_sales",
    )


# def create_std_drilled_sales_ops(
#     stock_code: str,
#     route: str = "6"   
# ) -> None:
    
#     dppick_row = bom.build_bomoperations_row(
#         values={
#             "StockCode": stock_code,
#             "Route": route,
#             "Operation": 1,
#             "WorkCentre": "DPPICK",
#             "Milestone": "Y"
#         }
#     )
    
#     dpchk_row = bom.build_bomoperations_row(
#         values={
#             "StockCode": stock_code,
#             "Route": route,
#             "Operation": 2,
#             "WorkCentre": "DPCHK",
#             "Milestone": "N"
#         }
#     )
    
#     dpdrl_row = bom.build_bomoperations_row(
#         values={
#             "StockCode": stock_code,
#             "Route": route,
#             "Operation": 3,
#             "WorkCentre": "DPDRL",
#             "Milestone": "Y"
#         }
#     )
    
#     dppack_row = bom.build_bomoperations_row(
#         values={
#             "StockCode": stock_code,
#             "Route": route,
#             "Operation": 4,
#             "WorkCentre": "DPPACK",
#             "Milestone": "Y"
#         }
#     )
    
#     dpdesp_row = bom.build_bomoperations_row(
#         values={
#             "StockCode": stock_code,
#             "Route": route,
#             "Operation": 5,
#             "WorkCentre": "DPDESP",
#             "Milestone": "Y"
#         }
#     )

#     ops_list = [dppick_row, dpchk_row, dpdrl_row, dppack_row, dpdesp_row]

#     sql.append_multiple_records(
#         table="BomOperations",
#         rows=ops_list
#     )


def create_std_sales_code_bom(
    parent_part: str,
    component: str,
    route: str = "6",
    skip_label: bool = False 
) -> None:
    
    material_row = bom.build_bomstructure_row(
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
        label_row = bom.build_bomstructure_row(
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
 