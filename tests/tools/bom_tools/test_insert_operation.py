from domain.bom.routing import insert_operation

def test():
    insert_operation(
        stock_code="FFPDMC001",
        route="0",
        work_centre="BRUTAL",
        op_number=6
    )