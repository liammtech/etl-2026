import pytest
from pyodbc import Row
from db.sql import update_records, get_multiple_records


def test_posting():
    update_records(
        table = "BomOperations",
        criteria = {
            "StockCode": "FFPDMC001",
            "Operation": (">", 2)
        },
        update_data= {
            "WorkCentre": "MONKEY"
        } 
    )

    return_val = get_multiple_records(
        table = "BomOperations",
        criteria = {
            "StockCode": "FFPDMC001"
        }  
    )

    print(return_val)


# def test_wildcard():
#     update_records(
#         table = "BomStructure",
#         criteria = {
#             "ParentPart": "SWCC012",
#             "Component": "GL%"

#         },
#         update_data= {
#             "QtyPer": 12,
#             "QtyPerEnt": 12
#         } 
#     )
