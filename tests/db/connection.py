import pyodbc
from db.connection import get_cursor

def test():
    assert type(get_cursor()) == pyodbc.Cursor

