from typing import Protocol
from fiscal_risk.io.raw_reader import Record

Row = dict[str, float | str | bool | None]

class AccountExtractor(Protocol):
    @property
    def report(self) -> str: ...

    def extract(self, records: list[Record]) -> Row: ...