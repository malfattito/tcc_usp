from fiscal_risk.config import PROCESSED_DIR, SICONFI_RAW_DIR
from fiscal_risk.consolidator import Consolidator
from fiscal_risk.extract.dca import DcaExtractor
from fiscal_risk.extract.rgf import RgfExtractor
from fiscal_risk.io.parquet_repository import ParquetRepository
from fiscal_risk.io.raw_reader import GzipJsonReader


def build_consolidator() -> Consolidator:
    return Consolidator(GzipJsonReader(), [DcaExtractor(), RgfExtractor()])


def consolidate_siconfi() -> None:
    frame = build_consolidator().consolidate(SICONFI_RAW_DIR)
    path = ParquetRepository(PROCESSED_DIR).save(frame, "siconfi")
    print(f"saved {path} with {len(frame)} rows")


if __name__ == "__main__":
    consolidate_siconfi()