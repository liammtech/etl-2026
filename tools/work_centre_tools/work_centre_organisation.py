from tools.sql import get_single_record

def get_work_centre_description(
    work_centre: str
) -> str:
    return get_single_record(
        table="BomWorkCentre",
        criteria={
            "WorkCentre": work_centre
        },
        return_columns=["Description"]
    )