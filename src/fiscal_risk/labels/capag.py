from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class CapagSource:
    file: str
    sheet: str
    header_row: int
    base_year: int
    code_column: str
    grade_column: str
    publication_order: int


SOURCES = (
    CapagSource(
        "capag_municipios_2018.xlsx", "capag_2018", 0, 2017, "Cod.IBGE", "Classificação_CAPAG", 0
    ),
    CapagSource(
        "capag_municipios_2019.xlsx",
        "Capag - Municípios 2019",
        0,
        2018,
        "Cod.IBGE",
        "Classificação da CAPAG",
        0,
    ),
    CapagSource(
        "capag_municipios_2020.xlsx",
        "CAPAG-Municipios (4)",
        0,
        2019,
        "Cod.IBGE",
        "Classificação da CAPAG",
        0,
    ),
    CapagSource(
        "capag_municipios_2021.xlsx", "capag_2020", 0, 2020, "Cod.IBGE", "Classificação_CAPAG", 1
    ),
    CapagSource("capag_municipios_2022_rev.xlsx", "capag", 0, 2021, "Cod.IBGE", "CAPAG_Oficial", 2),
    CapagSource(
        "capag_municipios_2023.xlsx",
        "capag 23 ano base 22",
        0,
        2022,
        "Cod.IBGE",
        "CAPAG_Oficial",
        3,
    ),
    CapagSource(
        "capag_municipios_2024_out.xlsx",
        "CAPAG Ano Base 2022",
        3,
        2022,
        "Código Município Completo",
        "CAPAG",
        4,
    ),
    CapagSource(
        "capag_municipios_2024_out.xlsx",
        "CAPAG Ano Base 2023",
        3,
        2023,
        "Código Município Completo",
        "CAPAG",
        4,
    ),
    CapagSource(
        "capag_municipios_2025_nov.xlsx",
        "CAPAG Ano Base 2023",
        3,
        2023,
        "Código Município Completo",
        "CAPAG",
        5,
    ),
    CapagSource(
        "capag_municipios_2025_nov.xlsx",
        "CAPAG Ano Base 2024",
        3,
        2024,
        "Código Município Completo",
        "CAPAG",
        5,
    ),
    CapagSource(
        "capag_municipios_2026_set.xlsx",
        "CAPAG Ano Base 2024",
        3,
        2024,
        "Código Município Completo",
        "CAPAG",
        6,
    ),
    CapagSource(
        "capag_municipios_2026_set.xlsx",
        "CAPAG Ano Base 2025",
        3,
        2025,
        "Código Município Completo",
        "CAPAG",
        6,
    ),
)

GRADE_ALIASES = {"N.D.": "n.d.", "N.E.": "n.e."}
HIGH_RISK_GRADES = frozenset({"C", "D"})
LOW_RISK_GRADES = frozenset({"A", "A+", "B", "B+"})


class CapagLabelLoader:
    def __init__(self, directory: Path, sources: tuple[CapagSource, ...] = SOURCES) -> None:
        self._directory = directory
        self._sources = sources

    def load(self) -> pd.DataFrame:
        frames = [self._read_source(source) for source in self._sources]
        stacked = pd.concat(frames, ignore_index=True)
        return self._prefer_original_publication(stacked)

    def _read_source(self, source: CapagSource) -> pd.DataFrame:
        sheet = pd.read_excel(self._directory / source.file, source.sheet, header=source.header_row)
        codes = pd.to_numeric(sheet[source.code_column], errors="coerce").astype("Int64")
        frame = pd.DataFrame(
            {
                "ibge_code": codes,
                "base_year": source.base_year,
                "grade": self._normalize_grade(sheet[source.grade_column]),
                "publication_order": source.publication_order,
            }
        )
        return frame.dropna(subset=["ibge_code"]).drop_duplicates("ibge_code")

    @staticmethod
    def _normalize_grade(grades: pd.Series) -> pd.Series:
        return grades.astype(str).str.strip().replace(GRADE_ALIASES)

    @staticmethod
    def _prefer_original_publication(stacked: pd.DataFrame) -> pd.DataFrame:
        ordered = stacked.sort_values(["ibge_code", "base_year", "publication_order"])
        groups = ordered.groupby(["ibge_code", "base_year"])
        original = groups.head(1)
        latest = groups.tail(1)[["ibge_code", "base_year", "grade", "publication_order"]]
        latest = latest.rename(
            columns={"grade": "grade_recalculated", "publication_order": "latest_order"}
        )
        merged = original.merge(latest, on=["ibge_code", "base_year"])
        same_publication = merged["publication_order"] == merged["latest_order"]
        merged.loc[same_publication, "grade_recalculated"] = pd.NA
        return merged.drop(columns=["publication_order", "latest_order"]).reset_index(drop=True)
