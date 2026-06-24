import workflows.bom.routings.sales_codes as ops

def test():
    ops.create_rigid_drilled_sales_code_ops(
        stock_code="RNBWMISC600",
        route=0
    )