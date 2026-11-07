"""Treino e comparação de modelos para os 3 cenários de antecedência do alerta.

Uso:
    python -m src.train

Saídas:
    reports/metricas_modelos.csv          -> comparação de todos os modelos/cenários
    reports/figures/*.png                 -> ROC, matriz de confusão, comparação
    models/model_<cenario>.joblib         -> melhor modelo baseado em árvores + metadados
"""
from __future__ import annotations

import json

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    average_precision_score,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from .config import FIG_DIR, MODELS_DIR, RANDOM_STATE, REPORTS_DIR, SCENARIOS, TEST_SIZE
from .data import columns_for_scenario, load_data, make_binary_target

# Colunas nominais (códigos numéricos sem ordem). Recebem One-Hot na Regressão Logística.
NOMINAL = [
    "Marital Status", "Application mode", "Course", "Previous qualification",
    "Nacionality", "Mother's qualification", "Father's qualification",
    "Mother's occupation", "Father's occupation",
]

TREE_MODELS = {"Random Forest", "XGBoost"}


def build_models(X: pd.DataFrame, y: pd.Series) -> dict[str, Pipeline]:
    nominal = [c for c in NOMINAL if c in X.columns]
    numeric = [c for c in X.columns if c not in nominal]
    pos_weight = (y == 0).sum() / (y == 1).sum()

    lr_pre = ColumnTransformer(
        [
            ("nom", OneHotEncoder(handle_unknown="ignore", min_frequency=10), nominal),
            ("num", StandardScaler(), numeric),
        ]
    )
    return {
        "Baseline (classe majoritária)": Pipeline([("clf", DummyClassifier(strategy="most_frequent"))]),
        "Regressão Logística": Pipeline(
            [("pre", lr_pre), ("clf", LogisticRegression(max_iter=3000, class_weight="balanced"))]
        ),
        "Random Forest": Pipeline(
            [
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=400, min_samples_leaf=3, class_weight="balanced_subsample",
                        n_jobs=-1, random_state=RANDOM_STATE,
                    ),
                )
            ]
        ),
        "XGBoost": Pipeline(
            [
                (
                    "clf",
                    XGBClassifier(
                        n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8,
                        colsample_bytree=0.8, scale_pos_weight=pos_weight,
                        eval_metric="logloss", random_state=RANDOM_STATE, n_jobs=-1,
                    ),
                )
            ]
        ),
    }


def evaluate(y_true, proba, threshold: float = 0.5) -> dict[str, float]:
    pred = (proba >= threshold).astype(int)
    return {
        "accuracy": accuracy_score(y_true, pred),
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred, zero_division=0),
        "f1": f1_score(y_true, pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, proba),
        "pr_auc": average_precision_score(y_true, proba),
    }


def best_threshold_f2(y_true, proba) -> float:
    """Limiar que maximiza F2 (recall pesa mais que precisão: perder um aluno em risco é pior)."""
    grid = np.linspace(0.1, 0.9, 81)
    scores = [fbeta_score(y_true, (proba >= t).astype(int), beta=2, zero_division=0) for t in grid]
    return float(grid[int(np.argmax(scores))])


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    y_all = make_binary_target(df)
    print(f"Registros: {len(df)} | Taxa de evasão: {y_all.mean():.1%}")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    rows = []

    for scen, scen_label in SCENARIOS.items():
        print(f"\n=== Cenário {scen}: {scen_label} ===")
        cols = columns_for_scenario(df, scen)
        X_tr, X_te, y_tr, y_te = train_test_split(
            df[cols], y_all, test_size=TEST_SIZE, stratify=y_all, random_state=RANDOM_STATE
        )
        models = build_models(X_tr, y_tr)
        fitted, test_proba = {}, {}

        for name, pipe in models.items():
            cvres = cross_validate(
                pipe, X_tr, y_tr, cv=cv, n_jobs=1,
                scoring={"f1": "f1", "recall": "recall", "roc_auc": "roc_auc"},
            )
            pipe.fit(X_tr, y_tr)
            proba = pipe.predict_proba(X_te)[:, 1]
            fitted[name], test_proba[name] = pipe, proba
            m = evaluate(y_te, proba)
            row = {
                "cenario": scen, "modelo": name,
                "cv_f1": cvres["test_f1"].mean(), "cv_f1_std": cvres["test_f1"].std(),
                "cv_recall": cvres["test_recall"].mean(), "cv_auc": cvres["test_roc_auc"].mean(),
                **{f"teste_{k}": v for k, v in m.items()},
            }
            rows.append(row)
            print(f"{name:32s} CV-F1={row['cv_f1']:.3f}  teste: F1={m['f1']:.3f} "
                  f"recall={m['recall']:.3f} AUC={m['roc_auc']:.3f}")

        # --- Escolha do modelo implantado: melhor CV-F1 entre os modelos de árvore (TreeSHAP) ---
        cand = [r for r in rows if r["cenario"] == scen and r["modelo"] in TREE_MODELS]
        best_name = max(cand, key=lambda r: r["cv_f1"])["modelo"]
        best = fitted[best_name]

        oof = cross_val_predict(models[best_name], X_tr, y_tr, cv=cv, method="predict_proba")[:, 1]
        thr = best_threshold_f2(y_tr, oof)
        tuned = evaluate(y_te, test_proba[best_name], thr)
        print(f"-> Implantado: {best_name} | limiar F2={thr:.2f} | teste recall={tuned['recall']:.3f} "
              f"precisão={tuned['precision']:.3f} F1={tuned['f1']:.3f}")

        for r in rows:
            if r["cenario"] == scen and r["modelo"] == best_name:
                r["implantado"] = True
                r["limiar_otimo_f2"] = thr
                r.update({f"teste_limiar_{k}": v for k, v in tuned.items()})

        # Figuras: ROC de todos os modelos e matriz de confusão do implantado
        fig, ax = plt.subplots(figsize=(6, 5))
        for name in fitted:
            if name.startswith("Baseline"):
                continue
            RocCurveDisplay.from_predictions(y_te, test_proba[name], name=name, ax=ax)
        ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
        ax.set_title(f"Curvas ROC - {scen_label}")
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"roc_{scen}.png", dpi=150)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(4.6, 4.2))
        ConfusionMatrixDisplay.from_predictions(
            y_te, (test_proba[best_name] >= thr).astype(int),
            display_labels=["Sem evasão", "Evasão"], cmap="Blues", ax=ax, colorbar=False,
        )
        ax.set_title(f"{best_name} (limiar {thr:.2f})\n{scen_label}", fontsize=10)
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"confusao_{scen}.png", dpi=150)
        plt.close(fig)

        # Persistência do modelo + metadados usados pelo app e pelo explain.py
        bundle = {
            "model": best, "model_name": best_name, "scenario": scen, "scenario_label": scen_label,
            "features": cols, "threshold": thr,
            "defaults": X_tr.median(numeric_only=True).to_dict(),
            "ranges": {c: (float(X_tr[c].min()), float(X_tr[c].max())) for c in cols},
            "test_metrics_default": evaluate(y_te, test_proba[best_name], 0.5),
            "test_metrics_tuned": tuned,
        }
        joblib.dump(bundle, MODELS_DIR / f"model_{scen}.joblib")
        X_te.assign(y_true=y_te.values).to_csv(MODELS_DIR / f"holdout_{scen}.csv", index=False)

    res = pd.DataFrame(rows)
    res.to_csv(REPORTS_DIR / "metricas_modelos.csv", index=False)

    # Figura-resumo: F1 e recall por modelo e cenário (conjunto de teste)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, metric, title in zip(axes, ["teste_f1", "teste_recall"], ["F1 (classe Evasão)", "Recall (classe Evasão)"]):
        pv = res.pivot(index="modelo", columns="cenario", values=metric)
        pv.plot.bar(ax=ax, rot=20)
        ax.set_title(title)
        ax.set_xlabel("")
        ax.set_ylim(0, 1)
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "comparacao_modelos.png", dpi=150)
    plt.close(fig)

    (REPORTS_DIR / "resumo.json").write_text(
        json.dumps({"n": len(df), "taxa_evasao": float(y_all.mean())}, indent=2), encoding="utf-8"
    )
    print("\nConcluído. Resultados em reports/ e models/")


if __name__ == "__main__":
    main()
