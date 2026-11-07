"""Explicabilidade global (SHAP) e auditoria de justiça por grupo.

Uso:
    python -m src.explain
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from .config import FIG_DIR, MODELS_DIR, REPORTS_DIR, SCENARIOS, SENSITIVE
from .predict import load_bundle, shap_values_for


def global_shap(scen: str) -> pd.DataFrame:
    b = load_bundle(scen)
    hold = pd.read_csv(MODELS_DIR / f"holdout_{scen}.csv")
    X = hold[b["features"]]
    sv = shap_values_for(b, X)

    plt.figure()
    shap.summary_plot(sv, X, show=False, max_display=15)
    plt.title(f"SHAP - fatores que mais influenciam a evasão\n({SCENARIOS[scen]})", fontsize=10)
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"shap_summary_{scen}.png", dpi=150, bbox_inches="tight")
    plt.close()

    imp = pd.DataFrame({"fator": b["features"], "importancia_media_abs_shap": np.abs(sv).mean(axis=0)})
    imp = imp.sort_values("importancia_media_abs_shap", ascending=False)
    imp.to_csv(REPORTS_DIR / f"importancia_shap_{scen}.csv", index=False)
    return imp


def fairness_audit(scen: str) -> pd.DataFrame:
    """Compara taxas de alerta, recall e falsos positivos entre grupos (apenas auditoria)."""
    b = load_bundle(scen)
    hold = pd.read_csv(MODELS_DIR / f"holdout_{scen}.csv")
    proba = b["model"].predict_proba(hold[b["features"]])[:, 1]
    pred = (proba >= b["threshold"]).astype(int)
    y = hold["y_true"].values

    rows = []
    for col, mapping in SENSITIVE.items():
        if col not in hold.columns:
            continue
        for val, label in mapping.items():
            m = hold[col].values == val
            if m.sum() < 20:
                continue
            tp = ((pred == 1) & (y == 1) & m).sum()
            fn = ((pred == 0) & (y == 1) & m).sum()
            fp = ((pred == 1) & (y == 0) & m).sum()
            tn = ((pred == 0) & (y == 0) & m).sum()
            rows.append(
                {
                    "cenario": scen, "atributo": col, "grupo": label, "n": int(m.sum()),
                    "taxa_real_evasao": y[m].mean(),
                    "taxa_de_alerta": pred[m].mean(),
                    "recall": tp / (tp + fn) if (tp + fn) else np.nan,
                    "precisao": tp / (tp + fp) if (tp + fp) else np.nan,
                    "falso_positivo_rate": fp / (fp + tn) if (fp + tn) else np.nan,
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(REPORTS_DIR / f"justica_{scen}.csv", index=False)

    if not df.empty:
        fig, axes = plt.subplots(1, 3, figsize=(13, 4))
        labels = df["atributo"] + ": " + df["grupo"]
        for ax, metric, title in zip(
            axes, ["taxa_de_alerta", "recall", "falso_positivo_rate"],
            ["Taxa de alerta", "Recall (evasões detectadas)", "Falsos positivos (taxa)"],
        ):
            ax.barh(labels, df[metric], color="#4C78A8")
            ax.set_title(title, fontsize=10)
            ax.set_xlim(0, 1)
            ax.grid(axis="x", alpha=0.3)
        fig.suptitle(f"Auditoria de justiça por grupo - {SCENARIOS[scen]}", fontsize=11)
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"justica_{scen}.png", dpi=150)
        plt.close(fig)
    return df


def main() -> None:
    for scen in SCENARIOS:
        print(f"\n=== {scen} ===")
        imp = global_shap(scen)
        print(imp.head(8).to_string(index=False))
        fa = fairness_audit(scen)
        if not fa.empty:
            print(fa.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
