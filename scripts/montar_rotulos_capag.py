"""Monta a tabela de rótulos CAPAG (município × ano-base) a partir das planilhas do Tesouro Transparente
em dados/raw/capag/. Para anos-base que reaparecem na publicação seguinte (recalculados com dados
reenviados e/ou metodologia nova), prevalece a PUBLICAÇÃO ORIGINAL, que foi a nota oficial vigente; a nota
recalculada fica em `capag_recalc`. Municípios ausentes da publicação original recebem a recalculada,
com `capag_origem = "recalc"`.

Uso:  python3 scripts/montar_rotulos_capag.py
Saída: dados/processed/capag_rotulos.parquet
    cod_ibge, ano_base, capag, capag_recalc, capag_origem, ind1, nota1, ind2, nota2, ind3, nota3, fonte
"""
import os, warnings
import pandas as pd

warnings.filterwarnings("ignore")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(RAIZ, "dados", "raw", "capag")
OUT = os.path.join(RAIZ, "dados", "processed", "capag_rotulos.parquet")

# (arquivo, aba, header, ano_base, col_codigo, col_capag, ordem de publicação)
FONTES = [
    ("capag_municipios_2018.xlsx", "capag_2018", 0, 2017, "Cod.IBGE", "Classificação_CAPAG", 0),
    ("capag_municipios_2019.xlsx", "Capag - Municípios 2019", 0, 2018, "Cod.IBGE", "Classificação da CAPAG", 0),
    ("capag_municipios_2020.xlsx", "CAPAG-Municipios (4)", 0, 2019, "Cod.IBGE", "Classificação da CAPAG", 0),
    ("capag_municipios_2021.xlsx", "capag_2020", 0, 2020, "Cod.IBGE", "Classificação_CAPAG", 1),
    ("capag_municipios_2022_rev.xlsx", "capag", 0, 2021, "Cod.IBGE", "CAPAG_Oficial", 2),
    ("capag_municipios_2023.xlsx", "capag 23 ano base 22", 0, 2022, "Cod.IBGE", "CAPAG_Oficial", 3),
    ("capag_municipios_2024_out.xlsx", "CAPAG Ano Base 2022", 3, 2022, "Código Município Completo", "CAPAG", 4),
    ("capag_municipios_2024_out.xlsx", "CAPAG Ano Base 2023", 3, 2023, "Código Município Completo", "CAPAG", 4),
    ("capag_municipios_2025_nov.xlsx", "CAPAG Ano Base 2023", 3, 2023, "Código Município Completo", "CAPAG", 5),
    ("capag_municipios_2025_nov.xlsx", "CAPAG Ano Base 2024", 3, 2024, "Código Município Completo", "CAPAG", 5),
    ("capag_municipios_2026_set.xlsx", "CAPAG Ano Base 2024", 3, 2024, "Código Município Completo", "CAPAG", 6),
    ("capag_municipios_2026_set.xlsx", "CAPAG Ano Base 2025", 3, 2025, "Código Município Completo", "CAPAG", 6),
]


def achar(df, *padroes):
    """Primeira coluna cujo nome normalizado bate com um dos padrões (ignora revisões/antigo)."""
    for pat in padroes:
        for c in df.columns:
            n = str(c).strip().lower().replace("_", " ")
            if n == pat.lower():
                return c
    return None


def main():
    partes = []
    for arq, aba, hdr, ano, ccod, ccapag, ordem in FONTES:
        df = pd.read_excel(os.path.join(RAW, arq), aba, header=hdr)
        df = df[df[ccod].notna()]
        out = pd.DataFrame({
            "cod_ibge": pd.to_numeric(df[ccod], errors="coerce").astype("Int64"),
            "ano_base": ano,
            "capag": df[ccapag].astype(str).str.strip().replace({"N.D.": "n.d.", "N.E.": "n.e."}),
            "ordem": ordem, "fonte": f"{arq}:{aba}",
        })
        for i in (1, 2, 3):
            ci = achar(df, f"indicador {i}", f"indicador_{i}")
            cn = achar(df, f"nota {i}", f"nota_{i}")
            out[f"ind{i}"] = pd.to_numeric(df[ci], errors="coerce").values if ci is not None else pd.NA
            out[f"nota{i}"] = df[cn].astype(str).str.strip().values if cn is not None else pd.NA
        out = out.dropna(subset=["cod_ibge"]).drop_duplicates("cod_ibge")
        print(f"{arq} [{aba}] ano-base {ano}: {len(out)} linhas; capag={out['capag'].value_counts().to_dict()}")
        partes.append(out)
    todas = pd.concat(partes, ignore_index=True)
    todas = todas.sort_values(["cod_ibge", "ano_base", "ordem"])
    ultimo = todas.groupby(["cod_ibge", "ano_base"]).head(1).copy()          # publicação original
    recalc = todas.groupby(["cod_ibge", "ano_base"]).tail(1)[["cod_ibge", "ano_base", "capag", "ordem"]] \
        .rename(columns={"capag": "capag_recalc", "ordem": "ordem_recalc"})
    ultimo = ultimo.merge(recalc, on=["cod_ibge", "ano_base"], how="left")
    ultimo["capag_origem"] = "original"
    mesma = ultimo["ordem"] == ultimo["ordem_recalc"]
    ultimo.loc[mesma, "capag_recalc"] = pd.NA
    # ano-base 2022: a publicação original (capag_municipios_2023) omite ~250 municípios; eles só existem na recalculada
    ultimo.loc[(ultimo["ano_base"] == 2022) & (ultimo["ordem"] == 4), "capag_origem"] = "recalc"
    ultimo = ultimo.drop(columns=["ordem", "ordem_recalc"])
    ultimo["capag"] = ultimo["capag"].replace({"nan": pd.NA, "None": pd.NA})
    ultimo.to_parquet(OUT, index=False)
    print("\nrótulos finais:", ultimo.shape)
    print(pd.crosstab(ultimo["ano_base"], ultimo["capag"].fillna("NA")))
    print("\norigem:", ultimo.groupby(["ano_base", "capag_origem"]).size().to_dict())
    rev = ultimo[ultimo["capag_recalc"].notna() & (ultimo["capag"] != ultimo["capag_recalc"])]
    print("notas que mudaram na recalculada:", len(rev), "de", ultimo["capag_recalc"].notna().sum())


if __name__ == "__main__":
    main()
