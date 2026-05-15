from tools.sql import get_single_record

def get_work_centre_description(
    work_centre: str
) -> str:
    work_centre_desc = get_single_record(
        table="BomWorkCentre",
        criteria={
            "WorkCentre": work_centre
        },
        return_columns=["Description"]
    )
    return work_centre_desc[0]