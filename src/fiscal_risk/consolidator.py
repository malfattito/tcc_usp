from collections import defaultdict
from pathlib import Path

import pandas as pd

from fiscal_risk.extract.base import AccountExtractor, Row
from fiscal_risk.io.raw_reader import RawReader

MunicipalityYear = tuple[int, int]


class Consolidator:
    def __init__(self, reader: RawReader, extractors: list[AccountExtractor]) -> None:
        self._reader = reader
        self._extractors = extractors

    def consolidate(self, root: Path) -> pd.DataFrame:
        rows: dict[MunicipalityYear, Row] = defaultdict(dict)
        for extractor in self._extractors:
            for path in sorted((root / extractor.report).glob("*/*.json.gz")):
                key = self._key_from_path(path)
                records = self._reader.read(path)
                rows[key][f"{extractor.report}_delivered"] = bool(records)
                rows[key].update(extractor.extract(records))
        return self._to_frame(rows)

    @staticmethod
    def _key_from_path(path: Path) -> MunicipalityYear:
        return int(path.stem.removesuffix(".json")), int(path.parent.name)

    @staticmethod
    def _to_frame(rows: dict[MunicipalityYear, Row]) -> pd.DataFrame:
        frame = pd.DataFrame(
            [{"ibge_code": code, "year": year, **row} for (code, year), row in rows.items()]
        )
        return frame.sort_values(["ibge_code", "year"]).reset_index(drop=True)
