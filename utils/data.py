from pyodbc import Row

def row_to_dict(row: Row) -> dict:
    return dict(zip([col[0] for col in row.cursor_description], row))