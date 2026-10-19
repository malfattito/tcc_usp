"""Monta a base de modelagem (município × ano t) juntando a tabela SICONFI consolidada e os rótulos CAPAG.

Uso:   python3 scripts/montar_base.py
Lê:    dados/processed/siconfi_municipio_ano.parquet, dados/processed/capag_rotulos.parquet
Salva: dados/processed/base_modelagem.parquet  e  dados/processed/base_dicionario.csv

Convenções
- Linha = município no exercício t (2019..2024). Variáveis explicativas são razões calculadas com as contas de t,
  defasagens (t-1, t-2) e variações; `capag_t` é a nota do ano-base t.
- Rótulos (t+1): `y_capag` = 1 se nota CAPAG do ano-base t+1 em {C, D}, 0 se em {A, A+, B, B+}, NaN se n.d./n.e.;
  `y_pessoal_rgf` = 1 se despesa com pessoal (RGF) >= 51,3% da RCL em t+1 (só quem publicou RGF);
  `pessoal_rcl_next` = razão pessoal/RCL aproximada pela DCA em t+1 (para limiar alternativo, todos os municípios).
- Contas de detalhe ausentes (ex.: operações de crédito, juros) valem zero; totais ausentes permanecem NaN.
"""
import csv, os
import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(RAIZ, "dados", "processed")

REGIAO = {1: "Norte", 2: "Nordeste", 3: "Sudeste", 4: "Sul", 5: "Centro-Oeste"}
ZERO_SE_AUSENTE = ["op_credito", "desp_juros", "desp_amortizacao", "desp_inversoes", "rec_capital", "transf_capital",
                   "ded_fundeb", "ded_transf_const", "ded_outras", "rp_nao_proc_inscritos", "rp_proc_inscritos",
                   "rec_contribuicoes", "rec_patrimonial", "rec_outras_correntes", "rec_iptu", "rec_iss"]

DIC = {}  # nome -> descrição


def razao(df, nome, num, den, desc):
    df[nome] = np.where(df[den].abs() > 0, df[num] / df[den], np.nan)
    DIC[nome] = desc


def main():
    s = pd.read_parquet(os.path.join(PROC, "siconfi_municipio_ano.parquet"))
    c = pd.read_parquet(os.path.join(PROC, "capag_rotulos.parquet"))
    s["cod_ibge"] = s["cod_ibge"].astype("int64"); c["cod_ibge"] = c["cod_ibge"].astype("int64")
    for col in ZERO_SE_AUSENTE:
        s[col] = s[col].fillna(0)
    # só municípios com DCA entregue (sem DCA não há variáveis)
    df = s[s["dca_entregue"]].copy()

    # ---- razões (DCA, todos os municípios) ----
    df["rcl_aprox"] = df["rec_corrente"] - df["ded_fundeb"] - df["ded_transf_const"] - df["ded_outras"]
    DIC["rcl_aprox"] = "Receita corrente líquida aproximada pela DCA: receita corrente menos deduções (FUNDEB, transf. constitucionais, outras)"
    razao(df, "pessoal_rcl", "desp_pessoal", "rcl_aprox", "Despesa com pessoal e encargos (DCA, empenhada) / RCL aproximada")
    razao(df, "pessoal_rc", "desp_pessoal", "rec_corrente", "Despesa com pessoal / receita corrente bruta")
    razao(df, "trib_rc", "rec_tributaria", "rec_corrente", "Receita tributária própria / receita corrente (autonomia)")
    razao(df, "transf_rc", "transf_correntes", "rec_corrente", "Transferências correntes / receita corrente (dependência)")
    razao(df, "transf_uniao_rc", "transf_uniao", "rec_corrente", "Transferências da União / receita corrente")
    razao(df, "transf_estados_rc", "transf_estados", "rec_corrente", "Transferências dos estados / receita corrente")
    df["poup_corrente"] = np.where(df["rec_corrente"] > 0, (df["rec_corrente"] - df["desp_corrente"]) / df["rec_corrente"], np.nan)
    DIC["poup_corrente"] = "Poupança corrente: (receita corrente - despesa corrente) / receita corrente"
    razao(df, "desp_corr_rcl", "desp_corrente", "rcl_aprox", "Despesa corrente / RCL aproximada (base do indicador 2 da CAPAG)")
    razao(df, "outras_corr_rcl", "desp_outras_correntes", "rcl_aprox", "Outras despesas correntes (custeio) / RCL aproximada")
    razao(df, "juros_rcl", "desp_juros", "rcl_aprox", "Juros e encargos da dívida / RCL aproximada")
    razao(df, "amort_rcl", "desp_amortizacao", "rcl_aprox", "Amortização da dívida / RCL aproximada")
    razao(df, "invest_dt", "desp_investimentos", "desp_total", "Investimentos / despesa total")
    razao(df, "capital_rc", "desp_capital", "rec_corrente", "Despesa de capital / receita corrente")
    razao(df, "op_credito_rc", "op_credito", "rec_corrente", "Operações de crédito / receita corrente")
    razao(df, "rp_np_rc", "rp_nao_proc_inscritos", "rec_corrente", "Restos a pagar não processados inscritos / receita corrente")
    razao(df, "rp_p_rc", "rp_proc_inscritos", "rec_corrente", "Restos a pagar processados inscritos / receita corrente")
    razao(df, "pago_emp", "desp_total_paga", "desp_total", "Despesa paga / despesa empenhada (execução financeira)")
    df["result_orc"] = np.where(df["rec_total_bruta"] > 0, (df["rec_total_bruta"] - df["desp_total"]) / df["rec_total_bruta"], np.nan)
    DIC["result_orc"] = "Resultado orçamentário: (receita total bruta - despesa total empenhada) / receita total bruta"
    df["rc_pc"] = np.where(df["populacao"] > 0, df["rec_corrente"] / df["populacao"], np.nan)
    DIC["rc_pc"] = "Receita corrente per capita (R$ correntes)"
    df["log_pop"] = np.log1p(df["populacao"]); DIC["log_pop"] = "log(1 + população)"
    df["porte"] = pd.cut(df["populacao"], [0, 5e3, 1e4, 2e4, 5e4, 1e5, 5e5, np.inf],
                         labels=["ate5k", "5-10k", "10-20k", "20-50k", "50-100k", "100-500k", "500k+"])
    DIC["porte"] = "Faixa populacional"
    df["regiao"] = (df["cod_ibge"] // 1_000_000).map(REGIAO); DIC["regiao"] = "Região geográfica (1º dígito do código IBGE)"

    # ---- razões do RGF (cobertura parcial) ----
    razao(df, "rgf_dcl_rcl", "rgf_dcl", "rgf_rcl", "Dívida consolidada líquida / RCL (RGF Anexo 02)")
    razao(df, "rgf_dc_rcl", "rgf_dc", "rgf_rcl", "Dívida consolidada / RCL (RGF Anexo 02)")
    razao(df, "rgf_caixa_liq_nv_rcl", "rgf_caixa_liquida_apos_rp_nv", "rgf_rcl", "Disponibilidade de caixa líquida após RP, recursos não vinculados / RCL (RGF Anexo 05)")
    razao(df, "rgf_caixa_bruta_nv_rcl", "rgf_caixa_bruta_nv", "rgf_rcl", "Disponibilidade de caixa bruta, recursos não vinculados / RCL")
    razao(df, "rgf_obrig_nv_rcl", "rgf_demais_obrig_nv", "rgf_rcl", "Demais obrigações financeiras, recursos não vinculados / RCL")
    DIC["rgf_pessoal_pct_rcl"] = "Despesa total com pessoal em % da RCL ajustada (RGF Anexo 01)"
    DIC["rgf_entregue"] = "Município publicou RGF do 3º quadrimestre no SICONFI"

    # ---- defasagens e variações ----
    df = df.sort_values(["cod_ibge", "ano"])
    g = df.groupby("cod_ibge")
    base_lag = ["pessoal_rcl", "trib_rc", "transf_rc", "poup_corrente", "desp_corr_rcl", "invest_dt", "rp_np_rc",
                "result_orc", "rgf_pessoal_pct_rcl", "rgf_dcl_rcl", "rgf_caixa_liq_nv_rcl"]
    for col in base_lag:
        for k in (1, 2):
            df[f"{col}_lag{k}"] = g[col].shift(k); DIC[f"{col}_lag{k}"] = f"{DIC[col]} em t-{k}"
        df[f"{col}_d1"] = df[col] - df[f"{col}_lag1"]; DIC[f"{col}_d1"] = f"Variação de {col} entre t-1 e t"
    for col in ("rec_corrente", "desp_pessoal", "desp_corrente"):
        prev = g[col].shift(1)
        df[f"var_{col}"] = np.where(prev > 0, df[col] / prev - 1, np.nan)
        DIC[f"var_{col}"] = f"Variação nominal de {col} entre t-1 e t"

    # ---- CAPAG em t (nota vigente) e rótulos em t+1 ----
    ct = c.rename(columns={"ano_base": "ano", "capag": "capag_t", "ind1": "capag_ind1_t", "ind2": "capag_ind2_t",
                           "ind3": "capag_ind3_t"})[["cod_ibge", "ano", "capag_t", "capag_ind1_t", "capag_ind2_t", "capag_ind3_t"]]
    df = df.merge(ct, on=["cod_ibge", "ano"], how="left")
    DIC.update({"capag_t": "Nota CAPAG do ano-base t", "capag_ind1_t": "Indicador 1 CAPAG (endividamento) ano-base t",
                "capag_ind2_t": "Indicador 2 CAPAG (poupança corrente) ano-base t", "capag_ind3_t": "Indicador 3 CAPAG (liquidez) ano-base t"})
    cn = c.assign(ano=c["ano_base"] - 1).rename(columns={"capag": "capag_next"})[["cod_ibge", "ano", "capag_next"]]
    df = df.merge(cn, on=["cod_ibge", "ano"], how="left")
    df["y_capag"] = df["capag_next"].map({"C": 1, "D": 1, "A": 0, "A+": 0, "B": 0, "B+": 0})
    nxt = s[["cod_ibge", "ano", "rgf_pessoal_pct_rcl", "desp_pessoal", "rec_corrente", "ded_fundeb", "ded_transf_const", "ded_outras"]].copy()
    nxt["ano"] = nxt["ano"] - 1
    nxt["rcl_next"] = nxt["rec_corrente"] - nxt["ded_fundeb"] - nxt["ded_transf_const"] - nxt["ded_outras"]
    nxt["pessoal_rcl_next"] = np.where(nxt["rcl_next"] > 0, nxt["desp_pessoal"] / nxt["rcl_next"], np.nan)
    nxt["y_pessoal_rgf"] = np.where(nxt["rgf_pessoal_pct_rcl"].notna(), (nxt["rgf_pessoal_pct_rcl"] >= 51.3).astype(float), np.nan)
    df = df.merge(nxt[["cod_ibge", "ano", "pessoal_rcl_next", "y_pessoal_rgf"]], on=["cod_ibge", "ano"], how="left")
    DIC.update({"capag_next": "Nota CAPAG do ano-base t+1 (rótulo bruto)", "y_capag": "1 = alto risco (C/D) em t+1; 0 = baixo (A/A+/B/B+); NaN = sem nota",
                "y_pessoal_rgf": "1 = pessoal >= 51,3% da RCL em t+1 pelo RGF", "pessoal_rcl_next": "Pessoal / RCL aproximada (DCA) em t+1"})

    df = df.sort_values(["cod_ibge", "ano"]).reset_index(drop=True)
    df.to_parquet(os.path.join(PROC, "base_modelagem.parquet"), index=False)
    with open(os.path.join(PROC, "base_dicionario.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["variavel", "descricao"])
        for k, v in DIC.items(): w.writerow([k, v])
    print("base:", df.shape)
    print("\nRótulo y_capag por ano t (rótulo = ano-base t+1):")
    print(pd.crosstab(df["ano"], df["y_capag"].fillna(-1).astype(int), margins=True))
    print("\nRótulo y_pessoal_rgf por ano t:")
    print(pd.crosstab(df["ano"], df["y_pessoal_rgf"].fillna(-1).astype(int)))
    feats = [k for k in DIC if k not in ("capag_next", "y_capag", "y_pessoal_rgf", "pessoal_rcl_next")]
    print("\nvariáveis explicativas:", len(feats))
    print("ausência média (%) nas variáveis, linhas com rótulo CAPAG:")
    m = df[df["y_capag"].notna()][feats].isna().mean().sort_values(ascending=False)
    print((m[m > 0.02] * 100).round(0).to_string())


if __name__ == "__main__":
    main()
