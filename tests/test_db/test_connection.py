import pyodbc
from db.connection import get_cursor, get_dev_cursor

def test():
    assert type(get_dev_cursor()) == pyodbc.Cursor

