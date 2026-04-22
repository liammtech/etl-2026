from tools.sql import delete_records

def test_delete_records():
    delete_records(
        table="BomStructure",
        criteria={
            "ParentPart": "SWCC%"
        }
    )