import db.sql as sql
from records.bom import build_bomoperations_row


def build_op_num_mapping(op_nums: list[int]) -> dict[int, int]:
    unique_sorted = sorted(set(op_nums))
    return {old: new for new, old in enumerate(unique_sorted, start=1)}


def defrag_routing(
    stock_code: str,
    route: str = "*"
):
    # One stock code, in one route, at a time
    
    # 1. Get list of op numbers
    route = str(route).strip()

    print(F"DEFRAGGING FOR ROUTE: {route}")

    op_nums = sql.get_multiple_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": route
        },
        return_columns={
            "Operation"
        }
    )

    op_nums = [int(i) for list in op_nums for i in list]
    op_nums.sort()

    mapping = build_op_num_mapping(op_nums=op_nums)

    for old_op, new_op in mapping.items():
        if old_op == new_op:
            continue

        sql.update_records(
            table="BomOperations",
            criteria={
                "StockCode": stock_code,
                "Route": route,
                "Operation": old_op
            },
            update_data={"Operation": new_op}
        )

        sql.update_records(
            table="[BomOperations+]",
            criteria={
                "StockCode": stock_code,
                "Route": route,
                "Operation": old_op
            },
            update_data={"Operation": new_op}
        )

        sql.update_records(
            table="BomStructure",
            criteria={
                "ParentPart": stock_code,
                "Route": route,
                "OperationOffset": old_op
            },
            update_data={"OperationOffset": new_op}
        )


def defrag_routing_multiple(
    range: list
) -> None:
    for i in range: 
        defrag_routing(i)


def get_next_op_number(
    stock_code: str,
    route: str = 0
) -> int:
    op_nums = sql.get_multiple_records(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": route
        },
        return_columns={
            "Operation"
        }
    )

    op_nums = [int(i) for list in op_nums for i in list]
    op_nums.sort()

    next_op = op_nums[-1] + 1

    return next_op


def check_if_work_centre_in_routing(
    stock_code: str,
    route: str,
    work_centre: str
) -> bool:
    """
    Check if a given work centre is present within the operations list for
    a stock code in a particular route.

    Args:
        stock_code: The stock code to check
        route: The operations routing to check
        work_centre: The work centre being checked to see if it is present

    Returns:
        bool: True if work centre is present, otherwise False
    """

    query_result = sql.get_single_record(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": route,
            "WorkCentre": work_centre
        }
    )

    return True if query_result else False


def check_if_work_centre_in_routing(
    stock_code: str,
    route: str,
    work_centre: str
) -> bool:
    """
    Check if a given work centre is present within the operations list for
    a stock code in a particular route.

    Args:
        stock_code: The stock code to check
        route: The operations routing to check
        work_centre: The work centre being checked to see if it is present

    Returns:
        bool: True if work centre is present, otherwise False
    """

    query_result = sql.get_single_record(
        table="BomOperations",
        criteria={
            "StockCode": stock_code,
            "Route": route,
            "WorkCentre": work_centre
        }
    )

    return True if query_result else False


def insert_operation(
    stock_code: str,
    route: str,
    work_centre: str,
    after_work_centre: str | None = None,
    op_number: int | None = None
) -> None:
    '''
    Inserts an operation at a specified position. Specify either the work
    centre to place the new op after, or a specified position (mutually exclusive).

    Note: If using after_work_centre and there are multiple instances of the same work centre
    already existing, it will insert after the first instance.

    Args:
        stock_code: The stock code to receive the new operation
        route: The route to insert the new operation into
        work_centre: The work centre to be inserted
        after_work_centre: Mutually exclusive with op_number. The work centre to follow with the new operation
        op_number: Mutually exclusive with after_work_centre. The operation number to place the new operation at

    Returns:
        None. Inserts a new operation as specified, incrementing any subsequent lines' op numbers by 1

    '''

    if (after_work_centre is None) == (op_number is None):
        raise ValueError("Exactly one of these parameters must be supplied: after_work_centre or op_number")
    
    prev_op = None

    if after_work_centre:
        prev_op = sql.get_single_record(
            table="BomOperations",
            criteria={
                "StockCode": stock_code,
                "Route": route,
                "WorkCentre": after_work_centre
            },
            return_columns=["Operation"],
            flatten=True
        )

        if not prev_op:
            print(f"{stock_code}: no {after_work_centre} work centre found in route {route}, skipping...")
            return

        op_number = prev_op + 1

    shift_from = op_number

    sql.shift_unique_sequence(
        table="BomOperations",
        sequence_column="Operation",
        criteria={
            "StockCode": stock_code,
            "Route": route,
            "Operation": (">=", shift_from),
        },
        delta=1
    )
        
    op_row = build_bomoperations_row(
        stock_code=stock_code,
        route=route,
        operation=op_number,
        work_centre=work_centre
    )

    sql.append_single_record(
        table="BomOperations",
        row=op_row
    )