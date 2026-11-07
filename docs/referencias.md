# Fontes e referências

Relação completa das fontes utilizadas no projeto: conjunto de dados, artigos científicos, bibliotecas de software, serviços de IA, legislação e ferramentas de apoio ao desenvolvimento.

---

## 1. Conjunto de dados e artigo de origem

| # | Fonte | Uso no projeto |
|---|---|---|
| D1 | REALINHO, V.; MACHADO, J.; BAPTISTA, L.; MARTINS, M. V. **Predict Students' Dropout and Academic Success** [conjunto de dados]. UCI Machine Learning Repository, 2021. DOI: [10.24432/C5MC89](https://doi.org/10.24432/C5MC89). Disponível em: https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success. Licença CC BY 4.0. | Conjunto de dados utilizado no treinamento e avaliação (`data/students_dropout.csv`) e metadados oficiais (`data/dicionario_de_variaveis.csv`) |
| D2 | REALINHO, V.; MACHADO, J.; BAPTISTA, L. M. T.; MARTINS, M. V. **Predicting Student Dropout and Academic Success**. *Data*, v. 7, n. 11, art. 146, 2022. DOI: [10.3390/data7110146](https://doi.org/10.3390/data7110146). | Descrição da coleta original (Instituto Politécnico de Portalegre, Portugal), definição das variáveis e contextualização do problema |

> Os registros são públicos e previamente anonimizados pelos autores originais. Nenhum dado pessoal foi coletado pelo grupo.

---

## 2. Bibliotecas e softwares utilizados

| Software | Versão | Função no projeto | Referência / documentação |
|---|---|---|---|
| Python | 3.13.14 | Linguagem principal | https://www.python.org |
| pandas | 3.1.1 | Manipulação e tabulação de dados | McKinney (2010); https://pandas.pydata.org |
| NumPy | 2.5.4 | Computação vetorial e numérica | Harris et al. (2020); https://numpy.org |
| scikit-learn | 1.9.1 | Pipelines, validação cruzada, Regressão Logística, Random Forest e métricas | Pedregosa et al. (2011); https://scikit-learn.org |
| XGBoost | 3.4.1 | Modelo de *gradient boosting* implantado | Chen e Guestrin (2016); https://xgboost.readthedocs.io |
| SHAP | 0.54.1 | Explicabilidade global e individual (`TreeSHAP`) | Lundberg e Lee (2017); Lundberg et al. (2020); https://shap.readthedocs.io |
| matplotlib | 3.11.2 | Geração das figuras de avaliação e EDA | Hunter (2007); https://matplotlib.org |
| seaborn | 0.13.2 | Visualizações estatísticas | Waskom (2021); https://seaborn.pydata.org |
| joblib | 1.6.0 | Serialização dos modelos treinados (`.joblib`) | https://joblib.readthedocs.io |
| ucimlrepo | 0.0.7 | Download programático do repositório UCI | https://github.com/uci-ml-repo/ucimlrepo |
| Streamlit | 1.67.0 | Interface web interativa (`app/app.py`) | https://docs.streamlit.io |
| Jupyter (`nbformat`, `nbconvert`, `ipykernel`) | 5.11.1 / 7.17.2 / 7.4.0 | Execução do notebook de resultados | https://jupyter.org |
| Mermaid | - | Diagramas de arquitetura e fluxo (`docs/arquitetura.md`) | https://mermaid.js.org |

---

## 3. Serviços e ferramentas de Inteligência Artificial

| Recurso | Finalidade | Observações |
|---|---|---|
| **Gemini API** (Google) | Geração opcional de resumo interpretativo no app (`app/app.py`, função `gemini_summary`) | Documentação: https://ai.google.dev/gemini-api/docs. Executada apenas quando `GEMINI_API_KEY` está configurada no ambiente; sem chave, o sistema opera integralmente de forma local |
| **Antigravity** (assistente de codificação com LLM) e busca web integrada | Apoio ao brainstorming, pesquisa de fontes, codificação e estruturação documental | Detalhamento completo das atividades e da verificação humana em [`uso_de_ia.md`](uso_de_ia.md) |

---

## 4. Referências bibliográficas (metodologia, modelos e ética)

**Aprendizado de máquina em dados tabulares**
- BREIMAN, L. Random Forests. *Machine Learning*, v. 45, n. 1, p. 5-32, 2001.
- CHEN, T.; GUESTRIN, C. XGBoost: A Scalable Tree Boosting System. In: *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 2016, p. 785-794. DOI: 10.1145/2939672.2939785.
- GRINSZTAJN, L.; OYALLON, E.; VAROQUAUX, G. Why do tree-based models still outperform deep learning on typical tabular data? In: *Advances in Neural Information Processing Systems (NeurIPS Datasets and Benchmarks)*, 2022.
- PEDREGOSA, F. et al. Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, v. 12, p. 2825-2830, 2011.

**Explicabilidade (XAI)**
- LUNDBERG, S. M.; LEE, S.-I. A Unified Approach to Interpreting Model Predictions. In: *Advances in Neural Information Processing Systems 30 (NeurIPS)*, 2017.
- LUNDBERG, S. M. et al. From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence*, v. 2, p. 56-67, 2020.

**Justiça algorítmica**
- BAROCAS, S.; HARDT, M.; NARAYANAN, A. *Fairness and Machine Learning: Limitations and Opportunities*. MIT Press, 2023. Disponível em: https://fairmlbook.org.

**Artigos de referência das bibliotecas científicas**
- MCKINNEY, W. Data Structures for Statistical Computing in Python. In: *Proceedings of the 9th Python in Science Conference*, 2010, p. 56-61.
- HARRIS, C. R. et al. Array programming with NumPy. *Nature*, v. 585, p. 357-362, 2020.
- HUNTER, J. D. Matplotlib: A 2D Graphics Environment. *Computing in Science & Engineering*, v. 9, n. 3, p. 90-95, 2007.
- WASKOM, M. L. seaborn: statistical data visualization. *Journal of Open Source Software*, v. 6, n. 60, 3021, 2021.

---

## 5. Legislação e referências institucionais

- BRASIL. **Lei nº 13.709, de 14 de agosto de 2018** (Lei Geral de Proteção de Dados Pessoais - LGPD). Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm.
- INEP - Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira. **Censo da Educação Superior**. Disponível em: https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/censo-da-educacao-superior.
