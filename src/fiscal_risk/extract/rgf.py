from fiscal_risk.extract.base import Row
from fiscal_risk.io.raw_reader import Record

PERSONNEL_ANNEX = "RGF-Anexo 01"
DEBT_ANNEX = "RGF-Anexo 02"
CASH_ANNEX = "RGF-Anexo 05"

PERSONNEL_ACCOUNTS = {
    ("DespesaComPessoalTotal", "Valor"): "rgf_personnel_total",
    ("DespesaComPessoalTotal", "% sobre a RCL Ajustada"): "rgf_personnel_pct_rcl",
    ("ReceitaCorrenteLiquidaLimiteLegal", "Valor"): "rgf_net_current_revenue",
    ("ReceitaCorrenteLiquidaAjustada", "Valor"): "rgf_adjusted_rcl",
}

DEBT_ACCOUNTS = {
    "DividaConsolidada": "rgf_consolidated_debt",
    "DividaConsolidadaLiquida": "rgf_net_consolidated_debt",
    "RGF2ReceitaCorrenteLiquida": "rgf_rcl_debt_annex",
    "PercentualDaDCLSobreARCL": "rgf_net_debt_pct_rcl",
}
DEBT_PERIOD_COLUMN = {"Q": "Até o 3º Quadrimestre", "S": "Até o 2º Semestre"}

CASH_LINE = "TOTAL DOS RECURSOS NÃO VINCULADOS (I)"
CASH_ACCOUNTS = {
    "DisponibilidadeDeCaixaBruta": "rgf_gross_cash",
    "DemaisObrigacoesFinanceiras": "rgf_other_obligations",
    "DisponibilidadeDeCaixaLiquidaAposRP": "rgf_net_cash_after_payables",
}


class RgfExtractor:
    @property
    def report(self) -> str:
        return "rgf"

    def extract(self, records: list[Record]) -> Row:
        if not records:
            return {}
        debt_column = DEBT_PERIOD_COLUMN[str(records[0]["periodicidade"])]
        row: Row = {}
        for record in records:
            column_name = self._output_column(record, debt_column)
            if column_name is not None:
                row[column_name] = record["valor"]
        return row

    @staticmethod
    def _output_column(record: Record, debt_column: str) -> str | None:
        annex = record["anexo"]
        code = record["cod_conta"]
        column = record["coluna"]
        if annex == PERSONNEL_ANNEX:
            return PERSONNEL_ACCOUNTS.get((code, column))
        if annex == DEBT_ANNEX and column == debt_column:
            return DEBT_ACCOUNTS.get(code)
        if annex == CASH_ANNEX and record["conta"] == CASH_LINE:
            return CASH_ACCOUNTS.get(code)
        return None
