# Registro de uso de Inteligência Artificial

Em atendimento ao requisito de **Uso responsável da IA** do trabalho, este documento registra quando e como recursos de Inteligência Artificial foram utilizados durante o desenvolvimento do projeto, bem como a verificação realizada pelo grupo.

## 1. Ferramentas de IA utilizadas no desenvolvimento

| Data | Ferramenta | Atividade | Verificação e atuação do grupo |
|---|---|---|---|
| 05/11/2026 | Assistente de IA (Antigravity / LLM) | Levantamento de ideias de temas e definição do escopo de ML | Avaliação de viabilidade conforme o prazo, foco em dados tabulares e disponibilidade de base pública aberta |
| 05/11/2026 | Assistente de IA e busca web integrada | Pesquisa do dataset UCI nº 697 e confirmação de DOI, autoria e licença | Conferência direta na página oficial do UCI Machine Learning Repository e no artigo de Realinho et al. (2022) |
| 05/11/2026 | Assistente de IA | Apoio na estruturação do código (`src/`, `app/`) e scripts de EDA, treinamento, SHAP e auditoria de justiça | Execução integral do pipeline, inspeção das métricas geradas, testes da interface Streamlit e ajustes de tipos de entrada |
| 05/11/2026 | Assistente de IA | Elaboração inicial da documentação técnica, diagramas Mermaid, relatório e estrutura de slides | Revisão do texto, substituição/conferência de todos os indicadores com as saídas reais em `reports/` e complementação de dados e autoria pelo grupo (05/11 a 07/11/2026) |

## 2. IA como componente da própria aplicação

| Componente | Abordagem de IA | Papel na solução |
|---|---|---|
| Classificador de risco de evasão | Aprendizado de máquina supervisionado (`XGBoost`, comparado com `Random Forest` e `Regressão Logística`) | Estima a probabilidade de evasão nos 3 cenários de antecedência |
| Explicabilidade local e global | `SHAP` (`TreeSHAP`) | Identifica e quantifica os fatores que aumentam ou reduzem o risco de cada estudante |
| Interpretação textual (opcional) | IA Generativa (`Gemini API`) | Redige sugestões pedagógicas neutras quando `GEMINI_API_KEY` está configurada, recebendo apenas nomes de fatores e contribuições (sem dados pessoais) |

## 3. Práticas de responsabilidade e mitigação de riscos
- **Reprodutibilidade:** todas as métricas reportadas provêm da execução real de `python -m src.train` e `python -m src.explain` (`random_state=42`), salvas em `reports/`.
- **Validação de código e resultados:** nenhum número ou gráfico foi aceito sem execução local, comparação contra *baseline* e teste automatizado da aplicação.
- **Privacidade:** nenhuma informação pessoal identificável é processada ou enviada a APIs externas; chaves de acesso não são versionadas no repositório (`.gitignore`).
- **Supervisão humana:** o sistema foi projetado estritamente como ferramenta de **apoio à decisão pedagógica**, nunca para decisões automatizadas sobre estudantes.
