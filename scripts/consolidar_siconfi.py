"""Consolida os arquivos brutos da API SICONFI (dados/raw/siconfi/{dca,rgf}/{ano}/{cod_ibge}.json.gz)
em uma tabela município × ano com as contas selecionadas, salva em parquet.

Uso:
    python3 scripts/consolidar_siconfi.py
Saída:
    dados/processed/siconfi_municipio_ano.parquet   (uma linha por município-ano, valores em R$ correntes)
    dados/processed/siconfi_dicionario.csv          (nome da coluna, origem, conta, coluna da API)

Lê um arquivo por vez (uso de memória < 1 GB). Contas ausentes no arquivo recebem NaN; para as contas de
detalhe (ex.: operações de crédito) a ausência significa valor zero e é tratada na montagem da base.
"""
import csv, glob, gzip, json, os
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(RAIZ, "dados", "raw", "siconfi")
OUT = os.path.join(RAIZ, "dados", "processed")

# ---- DCA Anexo I-C (receitas): cod_conta -> nome da coluna; coluna "Receitas Brutas Realizadas" ----
DCA_REC = {
    "ReceitasExcetoIntraOrcamentarias": "rec_total_bruta",
    "RO1.0.0.0.00.0.0": "rec_corrente",
    "RO1.1.0.0.00.0.0": "rec_tributaria",
    "RO1.1.1.2.50.0.0": "rec_iptu",
    "RO1.1.1.4.51.0.0": "rec_iss",
    "RO1.2.0.0.00.0.0": "rec_contribuicoes",
    "RO1.3.0.0.00.0.0": "rec_patrimonial",
    "RO1.7.0.0.00.0.0": "transf_correntes",
    "RO1.7.1.0.00.0.0": "transf_uniao",
    "RO1.7.2.0.00.0.0": "transf_estados",
    "RO1.9.0.0.00.0.0": "rec_outras_correntes",
    "RO2.0.0.0.00.0.0": "rec_capital",
    "RO2.1.0.0.00.0.0": "op_credito",
    "RO2.4.0.0.00.0.0": "transf_capital",
}
# Deduções da receita corrente (mesma conta RO1.0.0.0.00.0.0, outras colunas)
DCA_DED = {
    "Deduções - FUNDEB": "ded_fundeb",
    "Deduções - Transferências Constitucionais": "ded_transf_const",
    "Outras Deduções da Receita": "ded_outras",
}
# ---- DCA Anexo I-D (despesas por natureza): coluna "Despesas Empenhadas" ----
DCA_DESP = {
    "TotalDespesas": "desp_total",
    "DO3.0.00.00.00.00": "desp_corrente",
    "DO3.1.00.00.00.00": "desp_pessoal",
    "DO3.2.00.00.00.00": "desp_juros",
    "DO3.3.00.00.00.00": "desp_outras_correntes",
    "DO4.0.00.00.00.00": "desp_capital",
    "DO4.4.00.00.00.00": "desp_investimentos",
    "DO4.5.00.00.00.00": "desp_inversoes",
    "DO4.6.00.00.00.00": "desp_amortizacao",
}
DCA_DESP_COLS = {  # outras colunas do total da despesa
    "Despesas Liquidadas": "desp_total_liquidada",
    "Despesas Pagas": "desp_total_paga",
    "Inscrição de Restos a Pagar Não Processados": "rp_nao_proc_inscritos",
    "Inscrição de Restos a Pagar Processados": "rp_proc_inscritos",
}
# ---- RGF Anexo 01 (pessoal) ----
RGF01 = {
    ("DespesaComPessoalTotal", "Valor"): "rgf_pessoal_total",
    ("DespesaComPessoalTotal", "% sobre a RCL Ajustada"): "rgf_pessoal_pct_rcl",
    ("DespesaComPessoalBruta", "TOTAL (ÚLTIMOS 12 MESES) (a)"): "rgf_pessoal_bruta",
    ("ReceitaCorrenteLiquidaLimiteLegal", "Valor"): "rgf_rcl",
    ("ReceitaCorrenteLiquidaAjustada", "Valor"): "rgf_rcl_ajustada",
    ("LimiteMaximoDespesaComPessoalTotal", "% sobre a RCL Ajustada"): "rgf_limite_max_pct",
    ("LimitePrudencialDespesaComPessoalTotal", "% sobre a RCL Ajustada"): "rgf_limite_prud_pct",
}
# ---- RGF Anexo 02 (dívida) — coluna do último período ----
RGF02 = {
    "DividaConsolidada": "rgf_dc",
    "DividaConsolidadaLiquida": "rgf_dcl",
    "DeducoesDaDividaConsolidada": "rgf_dc_deducoes",
    "RGF2DisponibilidadeDeCaixa": "rgf_disp_caixa_a02",
    "RGF2ReceitaCorrenteLiquida": "rgf_rcl_a02",
    "PercentualDaDCSobreARCL": "rgf_dc_pct_rcl",
    "PercentualDaDCLSobreARCL": "rgf_dcl_pct_rcl",
    "RGF2DividaConsolidadaPrevidenciariaPassivoAtuarial": "rgf_passivo_atuarial",
}
RGF02_COL = {"Q": "Até o 3º Quadrimestre", "S": "Até o 2º Semestre"}
# ---- RGF Anexo 05 (disponibilidade de caixa e restos a pagar) — linhas de total ----
RGF05_LINHAS = {"TOTAL DOS RECURSOS NÃO VINCULADOS (I)": "nv", "TOTAL (III) = (I + II)": "tot",
                "TOTAL (IV) = (I + II + III)": "tot"}  # rótulo do total muda em 2023 (RPPS separado)
RGF05 = {
    "DisponibilidadeDeCaixaBruta": "caixa_bruta",
    "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores": "rp_liq_ant",
    "RestosAPagarLiquidadosENaoPagosDoExercicio": "rp_liq_exerc",
    "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores": "rp_nliq_ant",
    "DemaisObrigacoesFinanceiras": "demais_obrig",
    "DisponibilidadeDeCaixaLiquida": "caixa_liquida_antes_rp",
    "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio": "rp_nliq_exerc",
    "DisponibilidadeDeCaixaLiquidaAposRP": "caixa_liquida_apos_rp",
}


def ler(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def linha_dca(items):
    r = {}
    for i in items:
        cc, col, v = i["cod_conta"], i["coluna"], i["valor"]
        if i["anexo"] == "DCA-Anexo I-C":
            if col == "Receitas Brutas Realizadas" and cc in DCA_REC:
                r[DCA_REC[cc]] = v
            elif cc == "RO1.0.0.0.00.0.0" and col in DCA_DED:
                r[DCA_DED[col]] = v
        elif i["anexo"] == "DCA-Anexo I-D":
            if col == "Despesas Empenhadas" and cc in DCA_DESP:
                r[DCA_DESP[cc]] = v
            elif cc == "TotalDespesas" and col in DCA_DESP_COLS:
                r[DCA_DESP_COLS[col]] = v
    if items:
        r["populacao"] = items[0].get("populacao"); r["uf"] = items[0].get("uf")
        r["instituicao"] = items[0].get("instituicao")
    return r


def linha_rgf(items):
    r = {}
    if not items:
        return r
    r["rgf_periodicidade"] = items[0].get("periodicidade"); r["rgf_periodo"] = items[0].get("periodo")
    col02 = RGF02_COL.get(items[0].get("periodicidade"), "Até o 3º Quadrimestre")
    for i in items:
        cc, col, v = i["cod_conta"], i["coluna"], i["valor"]
        if i["anexo"] == "RGF-Anexo 01" and (cc, col) in RGF01:
            r[RGF01[(cc, col)]] = v
        elif i["anexo"] == "RGF-Anexo 02" and col == col02 and cc in RGF02:
            r[RGF02[cc]] = v
        elif i["anexo"] == "RGF-Anexo 05" and i["conta"] in RGF05_LINHAS and cc in RGF05:
            r[f"rgf_{RGF05[cc]}_{RGF05_LINHAS[i['conta']]}"] = v
    return r


def main():
    os.makedirs(OUT, exist_ok=True)
    linhas = {}
    for rel, fn in (("dca", linha_dca), ("rgf", linha_rgf)):
        for ano_dir in sorted(glob.glob(os.path.join(RAW, rel, "*"))):
            ano = int(os.path.basename(ano_dir)); n = 0
            for path in glob.glob(os.path.join(ano_dir, "*.json.gz")):
                cod = int(os.path.basename(path).split(".")[0])
                d = fn(ler(path))
                if rel == "dca":
                    d["dca_entregue"] = bool(d)
                else:
                    d["rgf_entregue"] = bool(d)
                linhas.setdefault((cod, ano), {}).update(d); n += 1
            print(f"{rel} {ano}: {n} arquivos")
    df = pd.DataFrame([{"cod_ibge": k[0], "ano": k[1], **v} for k, v in linhas.items()])
    df = df.sort_values(["cod_ibge", "ano"]).reset_index(drop=True)
    for c in df.columns:
        if c not in ("cod_ibge", "ano", "uf", "instituicao", "rgf_periodicidade", "dca_entregue", "rgf_entregue"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df.to_parquet(os.path.join(OUT, "siconfi_municipio_ano.parquet"), index=False)
    # dicionário
    with open(os.path.join(OUT, "siconfi_dicionario.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["coluna", "relatorio", "anexo", "cod_conta", "coluna_api"])
        for k, v in DCA_REC.items(): w.writerow([v, "DCA", "I-C", k, "Receitas Brutas Realizadas"])
        for k, v in DCA_DED.items(): w.writerow([v, "DCA", "I-C", "RO1.0.0.0.00.0.0", k])
        for k, v in DCA_DESP.items(): w.writerow([v, "DCA", "I-D", k, "Despesas Empenhadas"])
        for k, v in DCA_DESP_COLS.items(): w.writerow([v, "DCA", "I-D", "TotalDespesas", k])
        for (k, c), v in RGF01.items(): w.writerow([v, "RGF", "01", k, c])
        for k, v in RGF02.items(): w.writerow([v, "RGF", "02", k, "Até o 3º Quadrimestre / 2º Semestre"])
        for k, v in RGF05.items():
            for lin, suf in RGF05_LINHAS.items(): w.writerow([f"rgf_{v}_{suf}", "RGF", "05", k, lin])
    print(df.shape, "linhas x colunas; salvo em", OUT)
    print(df.groupby("ano")[["dca_entregue", "rgf_entregue"]].sum())
    print(df[["rec_corrente", "desp_pessoal", "rgf_pessoal_pct_rcl", "rgf_dcl_pct_rcl", "rgf_caixa_liquida_apos_rp_nv"]].describe().T)


if __name__ == "__main__":
    main()
