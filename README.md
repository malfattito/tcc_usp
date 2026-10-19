# Simulador web de risco fiscal de municípios brasileiros com aprendizado de máquina

Trabalho de Conclusão de Curso do MBA em Data Science e Analytics (USP/Esalq).
Autor: Silvano Maneck Malfatti.

O projeto treina modelos supervisionados para estimar, com um ano de antecedência, o risco fiscal de municípios
brasileiros, medido pela nota CAPAG da Secretaria do Tesouro Nacional, a partir das contas públicas do SICONFI, e
entrega um simulador web em que o gestor informa despesas previstas e recebe a estimativa de risco.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `src/fiscal_risk/` | pacote Python (preparação do dataset e, em seguida, modelos) |
| `tests/` | testes com pytest |
| `scripts/` | scripts de coleta (API SICONFI, planilhas CAPAG), consolidação e geração do projeto de pesquisa |
| `projeto_pesquisa/` | Projeto de Pesquisa no template do MBA |
| `referencias/` | catálogo das referências e PDFs de acesso aberto citados no texto |

Os dados brutos (API SICONFI e Tesouro Transparente) não são versionados; os scripts em `scripts/` os reconstroem.

## Ambiente

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```

## Fontes de dados

- CAPAG de municípios: <https://www.tesourotransparente.gov.br/ckan/dataset/capag-municipios>
- API SICONFI: <https://apidatalake.tesouro.gov.br/docs/siconfi/>
