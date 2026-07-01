from pyodbc import Row


def reduce_code_to_prefix(stock_code: str) -> str:

    code_prefix_arr = []

    for char in stock_code:
        if char.isnumeric():
            break
        code_prefix_arr.append(char)

    return "".join(code_prefix_arr)


def row_to_dict(row: Row) -> dict:
    return dict(zip([col[0] for col in row.cursor_description], row))