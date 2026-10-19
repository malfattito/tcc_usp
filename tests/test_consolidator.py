from pathlib import Path

from fiscal_risk.consolidator import Consolidator
from fiscal_risk.extract.dca import DcaExtractor
from fiscal_risk.extract.rgf import RgfExtractor
from fiscal_risk.io.raw_reader import Record


class FakeReader:
    """Devolve registros da memória, indexados por "relatório/arquivo", sem tocar no disco."""

    def __init__(self, contents: dict[str, list[Record]]) -> None:
        self._contents = contents

    def read(self, path: Path) -> list[Record]:
        return self._contents[f"{path.parent.parent.name}/{path.name}"]


def touch(root: Path, report: str, year: int, ibge_code: int) -> None:
    folder = root / report / str(year)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{ibge_code}.json.gz").touch()


def test_joins_dca_and_rgf_into_one_row_per_municipality_year(tmp_path):
    touch(tmp_path, "dca", 2022, 1100015)
    touch(tmp_path, "rgf", 2022, 1100015)
    reader = FakeReader(
        {
            "dca/1100015.json.gz": [
                {
                    "cod_conta": "RO1.0.0.0.00.0.0",
                    "coluna": "Receitas Brutas Realizadas",
                    "valor": 100.0,
                },
            ],
            "rgf/1100015.json.gz": [
                {
                    "anexo": "RGF-Anexo 01",
                    "cod_conta": "DespesaComPessoalTotal",
                    "coluna": "% sobre a RCL Ajustada",
                    "valor": 49.0,
                    "periodicidade": "Q",
                    "conta": "",
                },
            ],
        }
    )

    frame = Consolidator(reader, [DcaExtractor(), RgfExtractor()]).consolidate(tmp_path)

    assert len(frame) == 1
    row = frame.iloc[0]
    assert (row["ibge_code"], row["year"]) == (1100015, 2022)
    assert row["current_revenue"] == 100.0
    assert row["rgf_personnel_pct_rcl"] == 49.0
    assert bool(row["dca_delivered"]) and bool(row["rgf_delivered"])


def test_empty_rgf_file_marks_report_as_not_delivered(tmp_path):
    touch(tmp_path, "rgf", 2021, 3550308)
    reader = FakeReader({"rgf/3550308.json.gz": []})

    frame = Consolidator(reader, [RgfExtractor()]).consolidate(tmp_path)

    assert frame.loc[0, "rgf_delivered"] == False  # noqa: E712


def test_rows_are_sorted_by_code_and_year(tmp_path):
    for year in (2020, 2019):
        touch(tmp_path, "dca", year, 2)
    touch(tmp_path, "dca", 2019, 1)
    reader = FakeReader({"dca/1.json.gz": [], "dca/2.json.gz": []})

    frame = Consolidator(reader, [DcaExtractor()]).consolidate(tmp_path)

    assert list(zip(frame["ibge_code"], frame["year"])) == [(1, 2019), (2, 2019), (2, 2020)]
