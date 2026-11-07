"""AlertaEdu - aplicativo Streamlit de apoio à identificação precoce de risco de evasão.

Executar:  streamlit run app/app.py

Fontes: dataset Realinho et al. (2021), UCI, https://doi.org/10.24432/C5MC89; artigo Realinho et al.
(2022), Data 7(11):146, https://doi.org/10.3390/data7110146. Lista completa em docs/referencias.md.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import FIG_DIR, MODELS_DIR, SCENARIOS  # noqa: E402
from src.predict import explain_one, load_bundle, predict_risk  # noqa: E402

st.set_page_config(page_title="AlertaEdu", page_icon="🎓", layout="wide")

# ----------------------------------------------------------------------------- campos do formulário
BINARY = {
    "Gender": ("Sexo", {"Feminino": 0, "Masculino": 1}),
    "Scholarship holder": ("Bolsista", {"Não": 0, "Sim": 1}),
    "Debtor": ("Possui dívidas com a instituição", {"Não": 0, "Sim": 1}),
    "Tuition fees up to date": ("Mensalidades em dia", {"Não": 0, "Sim": 1}),
    "Displaced": ("Mora fora da cidade de origem (deslocado)", {"Não": 0, "Sim": 1}),
}
NUMERIC_BASE = ["Age at enrollment", "Admission grade", "Previous qualification (grade)"]
SEM_FIELDS = ["enrolled", "evaluations", "approved", "grade", "without evaluations"]
# Campos que são contagens inteiras no dataset (idade e número de disciplinas): exibidos como int.
INT_FIELDS = {"Age at enrollment"} | {
    f"Curricular units {s} sem ({k})" for s in ("1st", "2nd")
    for k in ("enrolled", "evaluations", "approved", "without evaluations")
}

LABELS_PT = {
    "Age at enrollment": "Idade na matrícula",
    "Admission grade": "Nota de admissão (0-200)",
    "Previous qualification (grade)": "Nota da formação anterior (0-200)",
}


def sem_field_label(col: str) -> str:
    sem = "1º sem." if "1st" in col else "2º sem."
    kind = col.split("(")[-1].rstrip(")")
    names = {
        "enrolled": "disciplinas matriculadas", "evaluations": "avaliações realizadas",
        "approved": "disciplinas aprovadas", "grade": "média das notas (0-20)",
        "without evaluations": "disciplinas sem avaliação",
    }
    return f"{sem}: {names.get(kind, kind)}"


def numeric_input(container, label: str, col: str, defaults: dict, ranges: dict):
    """number_input inteiro para contagens/idade (sem casas decimais) e decimal para notas."""
    lo, hi = ranges[col]
    if col in INT_FIELDS:
        return container.number_input(label, min_value=int(lo), max_value=int(hi),
                                      value=int(round(defaults[col])), step=1, format="%d", key=col)
    return container.number_input(label, min_value=float(lo), max_value=float(hi),
                                  value=float(defaults[col]), step=0.1, format="%.1f", key=col)


def gemini_summary(scenario_label: str, prob: float, factors: pd.DataFrame) -> str | None:
    """Texto opcional via Gemini. Envia SOMENTE nomes de fatores e contribuições (sem identificadores)."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    fatores = "\n".join(
        f"- {r.fator} = {r.valor:g} ({'aumenta' if r.contribuicao > 0 else 'reduz'} o risco)"
        for r in factors.itertuples()
    )
    prompt = (
        "Você apoia uma equipe pedagógica. Um modelo de ML estimou probabilidade de evasão de "
        f"{prob:.0%} para um aluno (momento: {scenario_label}). Principais fatores:\n{fatores}\n\n"
        "Escreva em português, em até 120 palavras, uma interpretação neutra e 3 ações de apoio "
        "(acolhimento, tutoria, auxílio). NÃO afirme que o aluno vai desistir, NÃO culpe o aluno, "
        "e lembre que a decisão é humana."
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    try:
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["candidates"][0]["content"]["parts"][0]["text"]
    except (urllib.error.URLError, KeyError, TimeoutError, json.JSONDecodeError):
        return None


def rule_based_summary(prob: float, factors: pd.DataFrame) -> str:
    up = [r.fator for r in factors.itertuples() if r.contribuicao > 0][:3]
    txt = f"O modelo estimou {prob:.0%} de probabilidade de evasão. "
    if up:
        txt += "Os fatores que mais aumentaram o risco foram: " + ", ".join(up) + ". "
    txt += ("Sugere-se contato de acolhimento, verificação de dificuldades acadêmicas/financeiras e "
            "encaminhamento a tutoria ou auxílio estudantil, sempre com decisão humana.")
    return txt


# ----------------------------------------------------------------------------- interface
st.title("🎓 AlertaEdu")
st.caption("Identificação precoce de alunos em risco de evasão - ferramenta de **apoio à decisão**, não de decisão automática.")

available = [s for s in SCENARIOS if (MODELS_DIR / f"model_{s}.joblib").exists()]
if not available:
    st.error("Nenhum modelo encontrado. Execute `python -m src.train` primeiro.")
    st.stop()

with st.sidebar:
    st.header("Configuração")
    scen = st.radio("Momento do alerta", available, index=min(1, len(available) - 1),
                    format_func=lambda s: SCENARIOS[s])
    st.info("Quanto mais cedo o alerta, mais tempo para agir - porém menor a precisão. "
            "Veja a comparação na aba *Sobre o modelo*.")
    st.warning("Dados do UCI (instituição portuguesa). Uso educacional; não validado para uso real "
               "no Brasil.")
    st.caption(
        "**Fontes:** dataset Realinho et al. (2021), UCI, doi:10.24432/C5MC89; artigo Realinho et al. "
        "(2022), *Data* 7(11):146, doi:10.3390/data7110146; XGBoost (Chen e Guestrin, 2016); "
        "SHAP (Lundberg e Lee, 2017). Lista completa em `docs/referencias.md`."
    )

bundle = load_bundle(scen)
features, defaults, ranges = bundle["features"], bundle["defaults"], bundle["ranges"]

tab1, tab2, tab3 = st.tabs(["👤 Aluno individual", "📄 Lote (CSV)", "📊 Sobre o modelo"])

# ---- Aba 1
with tab1:
    st.subheader(f"Simulação - {SCENARIOS[scen]}")
    values = dict(defaults)
    c1, c2, c3 = st.columns(3)
    cols_cycle = [c1, c2, c3]
    i = 0
    for col, (label, opts) in BINARY.items():
        if col in features:
            default_idx = int(defaults.get(col, 0))
            choice = cols_cycle[i % 3].selectbox(label, list(opts), index=default_idx, key=col)
            values[col] = opts[choice]
            i += 1
    for col in NUMERIC_BASE:
        if col in features:
            values[col] = numeric_input(cols_cycle[i % 3], LABELS_PT[col], col, defaults, ranges)
            i += 1

    for prefix, name in [("Curricular units 1st sem", "1º semestre"), ("Curricular units 2nd sem", "2º semestre")]:
        sem_cols = [c for c in features if c.startswith(prefix)
                    and c.split("(")[-1].rstrip(")") in SEM_FIELDS]
        if sem_cols:
            st.markdown(f"**Desempenho no {name}**")
            cc = st.columns(len(sem_cols))
            for k, col in enumerate(sem_cols):
                values[col] = numeric_input(cc[k], sem_field_label(col), col, defaults, ranges)

    st.caption("Demais variáveis (curso, escolaridade dos pais, indicadores econômicos etc.) usam a mediana "
               "do conjunto de treino. Para usar todos os campos, utilize a aba *Lote (CSV)*.")

    if st.button("Calcular risco", type="primary"):
        row = pd.DataFrame([values])[features]
        res = predict_risk(bundle, row).iloc[0]
        factors = explain_one(bundle, row, top_k=6)

        m1, m2, m3 = st.columns(3)
        m1.metric("Probabilidade de evasão", f"{res.prob_evasao:.0%}")
        m2.metric("Nível de risco", res.nivel_risco)
        m3.metric("Em alerta?", "Sim" if res.em_alerta else "Não")
        st.progress(float(res.prob_evasao))

        st.markdown("**Fatores que mais pesaram (SHAP)** - positivo aumenta o risco, negativo reduz")
        chart = factors.set_index("fator")["contribuicao"]
        st.bar_chart(chart)
        st.dataframe(factors, hide_index=True, width="stretch")

        st.markdown("**Interpretação sugerida**")
        text = gemini_summary(SCENARIOS[scen], res.prob_evasao, factors)
        if text:
            st.write(text)
            st.caption("Texto gerado por IA generativa (Gemini). Revise antes de usar.")
        else:
            st.write(rule_based_summary(res.prob_evasao, factors))
            st.caption("Defina GEMINI_API_KEY para gerar esta interpretação com um modelo de linguagem.")

# ---- Aba 2
with tab2:
    st.subheader("Análise em lote")
    st.write("Envie um CSV com as colunas do dataset (mesmos nomes). Colunas ausentes usam a mediana.")
    sample = MODELS_DIR / f"holdout_{scen}.csv"
    if sample.exists():
        st.download_button("Baixar CSV de exemplo", sample.read_bytes(), file_name=f"exemplo_{scen}.csv")
    up = st.file_uploader("CSV", type="csv")
    if up:
        df_in = pd.read_csv(up)
        for c in features:
            if c not in df_in.columns:
                df_in[c] = defaults.get(c, 0)
        out = pd.concat([df_in.reset_index(drop=True), predict_risk(bundle, df_in)], axis=1)
        out = out.sort_values("prob_evasao", ascending=False)
        st.metric("Alunos em alerta", f"{int(out['em_alerta'].sum())} de {len(out)}")
        st.dataframe(out[["prob_evasao", "nivel_risco", "em_alerta"] + features[:6]].head(200),
                     width="stretch")
        st.download_button("Baixar resultado", out.to_csv(index=False).encode(), "resultado_risco.csv")

# ---- Aba 3
with tab3:
    st.subheader(f"Modelo implantado: {bundle['model_name']}")
    tm = bundle["test_metrics_tuned"]
    a, b_, c, d, e = st.columns(5)
    a.metric("Recall", f"{tm['recall']:.2f}")
    b_.metric("Precisão", f"{tm['precision']:.2f}")
    c.metric("F1", f"{tm['f1']:.2f}")
    d.metric("ROC-AUC", f"{tm['roc_auc']:.2f}")
    e.metric("Limiar", f"{bundle['threshold']:.2f}")
    st.caption("Métricas no conjunto de teste (20% dos dados, nunca vistos no treino), classe 'Evasão'.")
    for name, cap in [(f"confusao_{scen}.png", "Matriz de confusão"), (f"roc_{scen}.png", "Curvas ROC"),
                      (f"shap_summary_{scen}.png", "Importância global (SHAP)"),
                      (f"justica_{scen}.png", "Auditoria de justiça por grupo"),
                      ("comparacao_modelos.png", "Comparação de modelos e cenários")]:
        p = FIG_DIR / name
        if p.exists():
            st.image(str(p), caption=cap)
