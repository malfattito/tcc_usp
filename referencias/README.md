# Referências — risco fiscal de municípios e aprendizado de máquina

Levantamento feito em 16 out 2026 (periódicos e anais, 2021 em diante, mais clássicos). Citações no formato do
item 19 do "Manual de Instruções e Normas" do MBA USP/Esalq (não é ABNT). ✔ = PDF nesta pasta, com o nome do
arquivo indicado. Os arquivos estão nomeados por autor, ano, veículo e tema.

Lembretes das normas: trabalhos de anais e preprints são aceitos apenas como apoio, não como fontes principais;
artigos devem ter até cinco anos, salvo obras clássicas.

## 1. Aprendizado de máquina para risco/estresse fiscal de governos locais

| ✔ | Referência | Para que serve |
|---|---|---|
| ✔ Garruti_Barboza_Diniz_2025_ASAA | Garruti, D.V.T.; Barboza, F.L.M.; Diniz, J.A. 2025. Utilização de inteligência artificial na previsão do estresse fiscal: evidências para municípios brasileiros. Advances in Scientific and Applied Accounting 17(3): 152-166. | Único brasileiro com ML (Random Forest, MG, 2016-2020, acurácia 68,2%). Comparação direta. |
| ✔ Radebe_Nomlala_Matenda_2026_Forecasting | Radebe, N.E.; Nomlala, B.C.; Matenda, F.R. 2026. Forecasting municipal financial distress in South Africa: a machine learning approach. Forecasting 8(1): 18. | Logística penalizada vs. Random Forest vs. XGBoost; validação temporal; SHAP; regra de capacidade "top 30". Modelo de desenho experimental. |
| ✔ Radebe_Nomlala_Matenda_2025_JRFM | Radebe, N.E.; Nomlala, B.C.; Matenda, F.R. 2025. Systematic review of financial distress prediction models for municipalities: key evaluation criteria and a framework for model selection. Journal of Risk and Financial Management 18(11): 624. | Revisão sistemática (24 artigos, 2000-2025) com dez critérios de avaliação de modelos. Ótima para a Introdução e para justificar métricas. |
|   | Liu, R.; Li, H.; Yoon, K. 2025. Using machine learning algorithms to improve fiscal distress prediction models: the case of U.S. local governments. Journal of Information Systems 39(3): 131-155. | Seis algoritmos e balanceamento de classes. Pago: baixar via Portal CAPES. |
|   | Antulov-Fantulin, N.; Lagravinese, R.; Resce, G. 2021. Predicting bankruptcy of local government: a machine learning approach. Journal of Economic Behavior and Organization 183: 681-699. | 7.795 municípios italianos; classes raras; variáveis não financeiras. Pago: Portal CAPES. |
|   | Agus, P.; Ridha, M.H.; Pramusetiyo, F.; Hidayat, R. 2025. Machine learning implementation to predict financial distress in local governments of Indonesia. Pacific Accounting Review (no prelo). DOI 10.1108/PAR-11-2024-0317. | 542 governos locais, 2013-2022; distress por déficit e cobertura da dívida; vários algoritmos por região. Pago: Portal CAPES. |
| ✔ Piermarini_Sudoso_Piccialli_2023_arXiv | Piermarini, D.; Sudoso, A.M.; Piccialli, V. 2023. Predicting municipalities in financial distress: a machine learning approach enhanced by domain expertise. arXiv:2302.05780. | Preprint (apoio): indicadores de auditores como features. |
| ✔ Chen_etal_2025_Brookings_MFC | Chen, C.; Zha, Y.; Ren, C.; Zhao, Y. 2025. Can machine learning algorithms better help predict fiscal stress in local governments? In: Municipal Finance Conference, 2025, Brookings Institution, Washington, DC, USA. | Conferência (apoio): métricas e desenho. |

## 2. Condição financeira, CAPAG e LRF no Brasil (2021 em diante)

| ✔ | Referência | Para que serve |
|---|---|---|
| ✔ Antunes_Silva_2025_DesenvQuestao | Antunes, R.M.C.; Silva, C.A.T. 2025. Indicadores socioeconômicos determinantes da condição financeira nos municípios brasileiros. Desenvolvimento em Questão 23(62): e15733. | CAPAG como medida de condição financeira (5.570 municípios, 2018-2021). |
| ✔ Antunes_etal_2024_ConTexto | Antunes, R.M.C.; Silva, M.C.; Vieira, L.M.E.R.; Lima, E.S. 2024. A influência do esforço tributário e da autossuficiência financeira na condição financeira de municípios brasileiros. ConTexto 24(57): 2-14. | CAPAG como variável dependente em 94 municípios grandes; autossuficiência financeira é significativa. |
| ✔ Batista_etal_2024_APGS | Batista, A.P.; Carvalho, T.F.M.; Macedo, M.A.S.; Cruz, C.F. 2024. Condição financeira dos municípios brasileiros no contexto da pandemia da Covid-19. Administração Pública e Gestão Social 16(1). | Índice de condição financeira com 20 indicadores do SICONFI; lista reaproveitável de features. |
| ✔ Lima_Boente_Stefanelli_2024_RAP | Lima, C.A.M.C.; Boente, D.R.; Stefanelli, N.O. 2024. Determinantes do cumprimento das despesas com pessoal e do resultado primário nos estados brasileiros: uma análise de 2017 a 2022. Revista de Administração Pública 58(3): e2023-0321. | Variável binária "cumpriu limite de pessoal"; estados. |
| ✔ Arraes_MatiasPereira_2024_RCGG | Arraes, J.P.S.; Matias-Pereira, J. 2024. Desvendando a influência da Lei de Responsabilidade Fiscal nos estados brasileiros: inferências quanto a sustentabilidade do endividamento, a eficiência do gasto com pessoal e a gestão fiscal responsável. Contabilidade, Gestão e Governança 27(1): 128-156. | Painel sobre LRF, pessoal e endividamento; revisão da literatura útil. Estados. |
| ✔ SalomaoNeto_Santos_2023_IPEA_PPP | Salomão Neto, B.A.; Santos, J.F.C. 2023. Dependência fiscal, ilusão fiscal e dificuldades orçamentárias nos municípios brasileiros: diagnóstico via modelos logit/probit. Planejamento e Políticas Públicas 64. | Logit/probit para estouro do limite prudencial (5.570 municípios, 1994-2017). Baseline estatístico. |
| ✔ Oliveira_Oliveira_2023_RAP | Oliveira, D.T.; Oliveira, A.G. 2023. (In)sustentabilidade financeira municipal: a frágil metodologia proposta pela PEC do Pacto Federativo. Revista de Administração Pública 57(5): e2023-0012. | Sustentabilidade de 5.570 municípios (2015-2020). |
| ✔ Marconato_Parre_Coelho_2021_RAP | Marconato, M.; Parré, J.L.; Coelho, M.H. 2021. Dinâmica financeira dos municípios brasileiros. Revista de Administração Pública 55(2): 378-394. | Painel 2002-2016: pessoal piora resultado fiscal; pequenos municípios industriais são os piores. |
| ✔ Sacramento_etal_2024_GestaoRegionalidade | Sacramento, A.R.S.; Raupp, F.M.; Almeida, D.R.; Lyrio Neto, A.A. 2024. Condição financeira governamental local: um estudo com municípios da Região Metropolitana de Salvador-Bahia. Gestão & Regionalidade 40: e20248516. | Teste dos dez pontos de Brown; heterogeneidade entre municípios vizinhos. |
| ✔ Silva_etal_2025_RCGG | Silva, G.I.A.; Mendes, N.C.F.; Cruz, E.R.N.; Arraes, J.P.S.; Costa, A.J.B. 2025. Análise do endividamento dos municípios baianos no período da pandemia da Covid-19. Contabilidade, Gestão e Governança 28(2): 686-709. | Endividamento municipal na pandemia (dez maiores municípios da BA). Contexto. |
| ✔ Silva_Machado_Quintana_2022_RSD | Silva, L.C.; Machado, D.P.; Quintana, A.C. 2022. Índice de risco fiscal municipal (IRFM): um instrumento para gestão de riscos em governos locais. Research, Society and Development 11(8): e32011831003. | Índice de risco fiscal para capitais; periódico de menor seletividade, usar com cautela. |
| ✔ Barros_Nossa_2022_EnANPAD | Barros, E.F.; Nossa, S.N. 2022. Índice da condição financeira municipal: uma proposta de índice para análise dos municípios brasileiros socioeconomicamente homogêneos. In: Encontro da ANPAD, 46, 2022, on-line. Anais... | Anais (apoio): análise fatorial e clusters em 325 municípios (2020). |

## 3. Clássicos e fundamentos (permitidos mesmo com mais de cinco anos)

- Gorina, E.; Maher, C.; Joffe, M. 2018. Local fiscal distress: measurement and prediction. Public Budgeting & Finance 38(1): 72-94.
- Trussel, J.M.; Patrick, P.A. 2009. A predictive model of fiscal distress in local governments. Journal of Public Budgeting, Accounting & Financial Management 21(4): 578-616. (conferir páginas)
- Cabaleiro, R.; Buch, E.; Vaamonde, A. 2013. Developing a method to assessing the municipal financial health. The American Review of Public Administration 43(6): 729-751. (conferir dados)
- Breiman, L. 2001. Random forests. Machine Learning 45(1): 5-32.
- ✔ Grinsztajn_Oyallon_Varoquaux_2022_NeurIPS_tabular — Grinsztajn, L.; Oyallon, E.; Varoquaux, G. 2022. Why do tree-based models still outperform deep learning on typical tabular data? Advances in Neural Information Processing Systems 35: 507-520. (justifica árvores em vez de aprendizado profundo em dados tabulares; PDF é a versão arXiv 2207.08815)
- ✔ ShwartzZiv_Armon_2022_InformationFusion_tabular — Shwartz-Ziv, R.; Armon, A. 2022. Tabular data: deep learning is not all you need. Information Fusion 81: 84-90. (mesma finalidade; PDF é a versão arXiv 2106.03253)
- Fávero, L.P.; Belfiore, P. 2017. Manual de Análise de Dados. Elsevier, Rio de Janeiro, RJ, Brasil.
- Hosmer, D.W.; Lemeshow, S.; Sturdivant, R.X. 2013. Applied Logistic Regression. 3ed. John Wiley & Sons, New York, NY, USA.
- Gil, A.C. 2017. Como Elaborar Projetos de Pesquisa. 6ed. Atlas, São Paulo, SP, Brasil.

## 4. Normativos e fontes de dados

- Brasil. 2000. Lei Complementar nº 101, de 4 de maio de 2000 (Lei de Responsabilidade Fiscal). Diário Oficial da União, Brasília, 5 maio 2000. Seção 1.
- Brasil. 2016. Conselho Nacional de Saúde. Resolução nº 510, de 7 de abril de 2016. Diário Oficial da União, Brasília, 24 maio 2016. Seção 1.
- Brasil. 2023. Ministério da Fazenda. Portaria Normativa MF nº 1.583, de 22 de dezembro de 2023 (metodologia da CAPAG). Diário Oficial da União, Brasília, dez. 2023. Seção 1.
- Secretaria do Tesouro Nacional [STN]. 2026. Capacidade de Pagamento de Municípios (CAPAG). Disponível em: <https://www.tesourotransparente.gov.br/ckan/dataset/capag-municipios>. Acesso em: 16 out. 2026.
- Secretaria do Tesouro Nacional [STN]. 2026. API SICONFI (Data Lake). Disponível em: <https://apidatalake.tesouro.gov.br/docs/siconfi/>. Acesso em: 16 out. 2026.

## 5. Não encontrados ou fora do critério

- Nenhum trabalho com aprendizado de máquina e finanças municipais foi localizado nos anais de EnANPAD, ANPCONT, Congresso USP ou SBPO de 2022 a 2025 pelas buscas feitas; vale repetir a busca diretamente nos repositórios desses eventos.
- Revista Contabilidade & Finanças: nenhum artigo municipal sobre LRF ou pessoal em 2021-2025 localizado.
- Pamba, D. (SSRN, 2025) sobre auditoria municipal na África do Sul: documento de trabalho, download bloqueado.

## 6. Onde continuar

Portal CAPES (biblioteca USP), SciELO, Google Acadêmico, BDTD e Biblioteca Pecege, com os termos: "fiscal distress"
OR "fiscal stress" AND "local government" AND "machine learning"; "despesa com pessoal" AND "Lei de Responsabilidade
Fiscal" AND municípios; "capacidade de pagamento" OR CAPAG; "condição financeira" AND municípios.
