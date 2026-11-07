# AlertaEdu - Identificação precoce de alunos em risco de evasão

Aplicação de **Aprendizado de Máquina** que estima a probabilidade de um aluno de ensino superior abandonar o curso, explica *por quê* (SHAP) e apoia a equipe pedagógica a agir cedo.

- **Disciplina:** AI
- **Integrantes:** José Henrique, Ryan Budin, João Pedro, Daniel Augusto, Matheus Miranda
- **Entrega:** 09/11/2026

## Estrutura do repositório

| Caminho | Conteúdo |
|---|---|
| `src/` | Código-fonte: carga de dados, EDA, treino, predição, SHAP e auditoria de justiça |
| `app/app.py` | Aplicativo Streamlit (individual, lote CSV, painel do modelo) |
| `data/` | Dataset utilizado (`students_dropout.csv`) e dicionário de variáveis |
| `models/` | Modelos treinados (`.joblib`) para os 3 cenários e amostras de teste |
| `reports/` | Métricas (`metricas_modelos.csv`), importâncias SHAP, auditoria de justiça e figuras |
| `docs/Relatorio_AlertaEdu.docx` | Relatório detalhado do projeto |
| `docs/AlertaEdu_slides.pptx` | Apresentação de slides do projeto |
| `docs/arquitetura.md` | Diagramas da arquitetura, do pipeline de ML e do fluxo do aplicativo |
| `docs/uso_de_ia.md` | Registro do uso responsável de IA no desenvolvimento |
| `docs/referencias.md` | Fontes, artigos, bibliotecas (com versões), serviços de IA e legislação |
| `notebooks/01_resultados.ipynb` | Notebook executável com a análise consolidada dos resultados |

## Como executar (Windows / PowerShell)

Requer Python 3.11+ (testado em 3.13).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Pipeline completo (baixa o dataset do UCI se não houver CSV local)
python -m src.eda        # análise exploratória -> reports/figures/eda_*.png
python -m src.train      # treina e compara modelos -> models/, reports/
python -m src.explain    # SHAP e auditoria de justiça -> reports/

# Aplicativo
streamlit run app/app.py
```

Ou tudo de uma vez: `.\run_all.ps1`.

Os modelos já treinados estão em `models/`, então o app roda direto sem precisar retreinar.

### Texto com IA generativa (opcional)
Para que o app gere a interpretação textual com o Gemini, defina a chave antes de abrir o app:

```powershell
$env:GEMINI_API_KEY = "sua-chave"
streamlit run app/app.py
```

Sem a chave, o app utiliza o resumo padrão baseado em regras. **A chave nunca deve ser colocada no código nem no repositório.**

## Resultados (conjunto de teste, classe "Evasão")

| Momento do alerta | Melhor modelo | ROC-AUC | Recall* | Precisão* |
|---|---|---|---|---|
| No ato da matrícula | XGBoost | 0,84 | 0,92 | 0,44 |
| Fim do 1º semestre | XGBoost | 0,91 | 0,88 | 0,58 |
| Fim do 2º semestre | XGBoost | 0,93 | 0,94 | 0,58 |

\* No limiar calibrado para priorizar recall (F2). Detalhes e comparação com Regressão Logística, Random Forest e baseline estão no relatório (`docs/Relatorio_AlertaEdu.docx`).

## Fontes e referências
- **Dataset:** REALINHO, V.; MACHADO, J.; BAPTISTA, L.; MARTINS, M. V. *Predict Students' Dropout and Academic Success*. UCI Machine Learning Repository, 2021. https://doi.org/10.24432/C5MC89 (licença CC BY 4.0).
- **Artigo associado:** REALINHO et al. Predicting Student Dropout and Academic Success. *Data*, 7(11), 146, 2022. https://doi.org/10.3390/data7110146
- **Lista completa de referências e bibliotecas:** [`docs/referencias.md`](docs/referencias.md).
- **Registro de uso de IA no desenvolvimento:** [`docs/uso_de_ia.md`](docs/uso_de_ia.md).

## Aviso
Projeto acadêmico. O modelo foi treinado com dados de uma instituição portuguesa e **não deve ser usado para decisões reais** sobre alunos sem validação local, avaliação ética e supervisão humana.
