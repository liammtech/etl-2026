import pytest
from pyodbc import Row
from tools.sql import update_records, get_multiple_records


def test_posting():
    update_records(
        table = "BomStructure",
        criteria = {
            "ParentPart": "SWCC012",
            "Component": "MEL0156"

        },
        update_data= {
            "QtyPer": 10,
            "QtyPerEnt": 10
        } 
    )

    return_val = get_multiple_records(
        table = "BomStructure",
        criteria = {
            "ParentPart": "SWCC012"
        }  
    )

    print(return_val)


def test_wildcard():
    update_records(
        table = "BomStructure",
        criteria = {
            "ParentPart": "SWCC012",
            "Component": "GL%"

        },
        update_data= {
            "QtyPer": 12,
            "QtyPerEnt": 12
        } 
    )
