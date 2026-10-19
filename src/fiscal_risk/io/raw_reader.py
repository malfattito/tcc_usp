import gzip
import json
from pathlib import Path
from typing import Protocol

Record = dict[str, object]


class RawReader(Protocol):
    def read(self, path: Path) -> list[Record]: ...


class GzipJsonReader:
    def read(self, path: Path) -> list[Record]:
        with gzip.open(path, "rt", encoding="utf-8") as file:
            return json.load(file)
