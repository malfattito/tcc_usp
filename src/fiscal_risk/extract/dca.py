from fiscal_risk.extract.base import Row
from fiscal_risk.io.raw_reader import Record

REVENUE_COLUMN = "Receitas Brutas Realizadas"
EXPENSE_COLUMN = "Despesas Empenhadas"
CURRENT_REVENUE_CODE = "RO1.0.0.0.00.0.0"
TOTAL_EXPENSE_CODE = "TotalDespesas"

REVENUE_ACCOUNTS = {
    "ReceitasExcetoIntraOrcamentarias": "total_revenue",
    "RO1.0.0.0.00.0.0": "current_revenue",
    "RO1.1.0.0.00.0.0": "tax_revenue",
    "RO1.7.0.0.00.0.0": "current_transfers",
    "RO1.7.1.0.00.0.0": "federal_transfers",
    "RO1.7.2.0.00.0.0": "state_transfers",
    "RO2.0.0.0.00.0.0": "capital_revenue",
    "RO2.1.0.0.00.0.0": "credit_operations",
}

REVENUE_DEDUCTIONS = {
    "Deduções - FUNDEB": "fundeb_deduction",
    "Deduções - Transferências Constitucionais": "constitutional_deduction",
    "Outras Deduções da Receita": "other_deductions",
}

EXPENSE_ACCOUNTS = {
    "TotalDespesas": "total_expense",
    "DO3.0.00.00.00.00": "current_expense",
    "DO3.1.00.00.00.00": "personnel_expense",
    "DO3.2.00.00.00.00": "interest_expense",
    "DO3.3.00.00.00.00": "other_current_expense",
    "DO4.0.00.00.00.00": "capital_expense",
    "DO4.4.00.00.00.00": "investment_expense",
    "DO4.6.00.00.00.00": "amortization_expense",
}


class DcaExtractor:
    @property
    def report(self) -> str:
        return "dca"

    def extract(self, records: list[Record]) -> Row:
        row: Row = {}
        for record in records:
            column_name = self._output_column(record)
            if column_name is not None:
                row[column_name] = record["valor"]
        return row

    @staticmethod
    def _output_column(record: Record) -> str | None:
        code = record["cod_conta"]
        column = record["coluna"]
        if column == REVENUE_COLUMN and code in REVENUE_ACCOUNTS:
            return REVENUE_ACCOUNTS[code]
        if code == CURRENT_REVENUE_CODE and column in REVENUE_DEDUCTIONS:
            return REVENUE_DEDUCTIONS[column]
        if column == EXPENSE_COLUMN and code in EXPENSE_ACCOUNTS:
            return EXPENSE_ACCOUNTS[code]
        return None
