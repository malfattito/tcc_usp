import pandas as pd

from fiscal_risk.labels.capag import CapagLabelLoader, CapagSource


def write_sheet(path, sheet: str, rows: list[dict], header_row: int = 0) -> None:
    frame = pd.DataFrame(rows)
    with pd.ExcelWriter(path, engine="openpyxl", mode="a" if path.exists() else "w") as writer:
        frame.to_excel(writer, sheet_name=sheet, index=False, startrow=header_row)


def test_normalizes_grade_aliases_and_drops_rows_without_code(tmp_path):
    write_sheet(
        tmp_path / "a.xlsx",
        "s",
        [
            {"Cod.IBGE": 1, "Nota": " A "},
            {"Cod.IBGE": 2, "Nota": "N.D."},
            {"Cod.IBGE": None, "Nota": "C"},
        ],
    )
    sources = (CapagSource("a.xlsx", "s", 0, 2020, "Cod.IBGE", "Nota", 1),)

    labels = CapagLabelLoader(tmp_path, sources).load()

    assert list(labels["ibge_code"]) == [1, 2]
    assert list(labels["grade"]) == ["A", "n.d."]
    assert labels["grade_recalculated"].isna().all()


def test_keeps_original_grade_and_stores_recalculated_one(tmp_path):
    write_sheet(tmp_path / "first.xlsx", "s", [{"Cod.IBGE": 1, "Nota": "B"}])
    write_sheet(tmp_path / "second.xlsx", "s", [{"Cod.IBGE": 1, "Nota": "C"}], header_row=3)
    sources = (
        CapagSource("second.xlsx", "s", 3, 2022, "Cod.IBGE", "Nota", 2),
        CapagSource("first.xlsx", "s", 0, 2022, "Cod.IBGE", "Nota", 1),
    )

    labels = CapagLabelLoader(tmp_path, sources).load()

    assert len(labels) == 1
    assert labels.loc[0, "grade"] == "B"
    assert labels.loc[0, "grade_recalculated"] == "C"
    assert set(labels.columns) == {"ibge_code", "base_year", "grade", "grade_recalculated"}
