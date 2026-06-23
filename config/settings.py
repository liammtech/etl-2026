# config/settings.py

from dotenv import load_dotenv
import os

load_dotenv()

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASILISC_ARGS_FILE = PROJECT_ROOT / "config" / "arguments" / "basilisc_args.yml"
