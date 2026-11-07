# Arquitetura da solução

## Visão geral

```mermaid
flowchart LR
    A[(UCI Dataset<br/>4.424 alunos)] --> B[src/data.py<br/>carga + alvo binário]
    B --> C[src/eda.py<br/>análise exploratória]
    B --> D[src/train.py<br/>3 cenários x 4 modelos<br/>validação cruzada]
    D --> E[(models/*.joblib<br/>melhor modelo + limiar)]
    D --> F[reports/<br/>métricas e figuras]
    E --> G[src/explain.py<br/>SHAP global + justiça]
    E --> H[src/predict.py<br/>risco + SHAP individual]
    H --> I[app/app.py<br/>Streamlit]
    I -.opcional.-> J[Gemini API<br/>texto de interpretação]
    I --> K[Coordenação / equipe pedagógica]
```

## Fluxo do pipeline de ML

```mermaid
flowchart TD
    S([Início]) --> L[Carregar dataset UCI]
    L --> T[Alvo binário: Dropout = 1]
    T --> SC{Cenário de alerta}
    SC -->|A| A1[Sem notas]
    SC -->|B| A2[Até 1º semestre]
    SC -->|C| A3[Até 2º semestre]
    A1 & A2 & A3 --> SP[Split 80/20 estratificado]
    SP --> CV[Validação cruzada 5-fold no treino]
    CV --> M[Baseline, Reg. Logística,<br/>Random Forest, XGBoost]
    M --> SEL[Seleção: melhor F1 em CV<br/>entre modelos de árvore]
    SEL --> THR[Limiar que maximiza F2<br/>previsões out-of-fold]
    THR --> TEST[Avaliação no teste]
    TEST --> SAVE[Salvar modelo + metadados]
    SAVE --> XAI[SHAP + auditoria de justiça]
```

## Fluxo de uso no aplicativo

```mermaid
sequenceDiagram
    actor U as Coordenador
    participant App as Streamlit
    participant M as Modelo (XGBoost/RF)
    participant S as SHAP
    participant G as Gemini (opcional)
    U->>App: Informa dados do aluno e o momento do alerta
    App->>M: predict_proba
    M-->>App: probabilidade de evasão
    App->>S: explicar previsão
    S-->>App: fatores que mais pesaram
    App->>G: apenas fatores + contribuições (sem identificação)
    G-->>App: texto de interpretação e ações de apoio
    App-->>U: risco, fatores e sugestões (decisão final humana)
```

## Decisões de projeto

| Decisão | Justificativa |
|---|---|
| Alvo binário (Dropout vs. demais) | Foco no que gera ação: identificar quem pode evadir |
| 3 cenários de antecedência | Mostra o trade-off entre precisão e tempo para intervir; evita "vazamento" de informação tardia |
| Modelos de árvore para implantação | Bom desempenho em dados tabulares e SHAP exato e rápido (TreeSHAP) |
| Limiar otimizado por F2 | Falso negativo (aluno em risco não detectado) é mais custoso que falso positivo |
| Auditoria de justiça | Atributos sensíveis não são regra de decisão, mas o desempenho por grupo é monitorado |
| LLM opcional e desacoplado | O sistema funciona sem serviço externo; privacidade preservada |
