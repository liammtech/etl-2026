import os
import pyodbc
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

def _need(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

def get_cursor():
    conn = pyodbc.connect(
        f"DRIVER={_need('DRIVER')};"
        f"SERVER={_need('SERVER')};"
        f"DATABASE={_need('DATABASE')};"
        f"Trusted_Connection={os.getenv('TRUSTED_CONNECTION','yes')};"
        f"Encrypt={os.getenv('ENCRYPT','yes')};"
        f"TrustServerCertificate={os.getenv('TRUST_SERVER_CERTIFICATE','no')};"
    )
    return conn.cursor()