from tools.bom_tools.bom_organisation import specify_edged_sides

def test_specify_sides_edged():
    specify_edged_sides(
        no_edged_sides = 2,
        stock_code = "GooGoo"
    )

    