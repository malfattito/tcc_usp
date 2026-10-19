from fiscal_risk.extract.dca import DcaExtractor


def make_record(code: str, column: str, value: float) -> dict:
    return {"cod_conta": code, "coluna": column, "valor": value}


def test_report_name_is_dca():
    assert DcaExtractor().report == "dca"


def test_extracts_revenue_deduction_and_expense():
    records = [
        make_record("RO1.0.0.0.00.0.0", "Receitas Brutas Realizadas", 100.0),
        make_record("RO1.0.0.0.00.0.0", "Deduções - FUNDEB", 10.0),
        make_record("DO3.1.00.00.00.00", "Despesas Empenhadas", 40.0),
        make_record("DO3.1.00.00.00.00", "Despesas Pagas", 35.0),
        make_record("RO9.9.9.9.99.9.9", "Receitas Brutas Realizadas", 1.0),
    ]

    row = DcaExtractor().extract(records)

    assert row == {
        "current_revenue": 100.0,
        "fundeb_deduction": 10.0,
        "personnel_expense": 40.0,
    }


def test_empty_records_give_empty_row():
    assert DcaExtractor().extract([]) == {}
