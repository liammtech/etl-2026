from workflows.bom.routings import create_std_drilled_sales_code_ops

def test():
    create_std_drilled_sales_code_ops(
        stock_code="HELLOTHERE",
        route=6
    )