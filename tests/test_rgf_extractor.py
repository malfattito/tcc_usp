from fiscal_risk.extract.rgf import RgfExtractor


def make_record(annex: str, code: str, column: str, value: float, **extra) -> dict:
    return {
        "anexo": annex,
        "cod_conta": code,
        "coluna": column,
        "valor": value,
        "periodicidade": "Q",
        "conta": "",
        **extra,
    }


def test_report_name_is_rgf():
    assert RgfExtractor().report == "rgf"


def test_extracts_one_value_from_each_annex():
    records = [
        make_record("RGF-Anexo 01", "DespesaComPessoalTotal", "% sobre a RCL Ajustada", 52.1),
        make_record("RGF-Anexo 01", "DespesaComPessoalTotal", "<MR-3>", 9.0),
        make_record("RGF-Anexo 02", "DividaConsolidada", "Até o 3º Quadrimestre", 300.0),
        make_record("RGF-Anexo 02", "DividaConsolidada", "Até o 1º Quadrimestre", 280.0),
        make_record(
            "RGF-Anexo 05",
            "DisponibilidadeDeCaixaBruta",
            "DISPONIBILIDADE DE CAIXA BRUTA (a)",
            50.0,
            conta="TOTAL DOS RECURSOS NÃO VINCULADOS (I)",
        ),
        make_record(
            "RGF-Anexo 05",
            "DisponibilidadeDeCaixaBruta",
            "DISPONIBILIDADE DE CAIXA BRUTA (a)",
            7.0,
            conta="Transferências do FUNDEB",
        ),
    ]

    row = RgfExtractor().extract(records)

    assert row == {
        "rgf_personnel_pct_rcl": 52.1,
        "rgf_consolidated_debt": 300.0,
        "rgf_gross_cash": 50.0,
    }


def test_semiannual_report_uses_second_semester_column():
    records = [
        make_record(
            "RGF-Anexo 02", "DividaConsolidada", "Até o 2º Semestre", 120.0, periodicidade="S"
        ),
    ]

    assert RgfExtractor().extract(records) == {"rgf_consolidated_debt": 120.0}


def test_empty_records_give_empty_row():
    assert RgfExtractor().extract([]) == {}
