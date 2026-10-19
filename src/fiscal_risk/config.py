from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "dados"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_DIR = DATA_DIR / "raw"
SICONFI_RAW_DIR = RAW_DIR / "siconfi"
CAPAG_RAWvier_DIR = RAW_DIR / "capag"

FIRST_YEAR = 2017
LAST_YEAR = 2025

