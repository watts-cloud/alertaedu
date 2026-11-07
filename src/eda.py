"""Análise exploratória (EDA) - gera figuras e estatísticas em reports/.

Uso:
    python -m src.eda
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .config import FIG_DIR, REPORTS_DIR, TARGET
from .data import load_data, make_binary_target


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    y = make_binary_target(df)

    # 1) Distribuição da variável-alvo
    counts = df[TARGET].value_counts()
    fig, ax = plt.subplots(figsize=(5, 3.5))
    counts.plot.bar(ax=ax, color=["#4C78A8", "#F58518", "#54A24B"], rot=0)
    for i, v in enumerate(counts):
        ax.text(i, v + 20, f"{v} ({v / len(df):.0%})", ha="center", fontsize=9)
    ax.set_title("Distribuição da situação do aluno")
    ax.set_ylabel("Alunos")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "eda_target.png", dpi=150)
    plt.close(fig)

    # 2) Evasão por situação financeira e bolsa
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    for ax, col, labels in zip(
        axes,
        ["Tuition fees up to date", "Scholarship holder", "Debtor"],
        [["Em atraso", "Em dia"], ["Não bolsista", "Bolsista"], ["Não devedor", "Devedor"]],
    ):
        rate = y.groupby(df[col]).mean()
        ax.bar(labels, rate.values, color="#E45756")
        for i, v in enumerate(rate.values):
            ax.text(i, v + 0.01, f"{v:.0%}", ha="center")
        ax.set_title(col, fontsize=10)
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("Taxa de evasão")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "eda_financeiro.png", dpi=150)
    plt.close(fig)

    # 3) Desempenho no 1º semestre vs. evasão
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    sns.boxplot(x=df[TARGET], y=df["Curricular units 1st sem (approved)"], ax=axes[0], order=["Dropout", "Enrolled", "Graduate"])
    axes[0].set_title("Disciplinas aprovadas no 1º semestre")
    axes[0].set_xlabel("")
    sns.boxplot(x=df[TARGET], y=df["Curricular units 1st sem (grade)"], ax=axes[1], order=["Dropout", "Enrolled", "Graduate"])
    axes[1].set_title("Média de notas no 1º semestre")
    axes[1].set_xlabel("")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "eda_semestre1.png", dpi=150)
    plt.close(fig)

    # 4) Idade na matrícula
    fig, ax = plt.subplots(figsize=(6, 3.6))
    sns.histplot(data=df.assign(Evasao=y.map({0: "Não", 1: "Sim"})), x="Age at enrollment",
                 hue="Evasao", bins=30, multiple="layer", alpha=0.55, ax=ax)
    ax.set_title("Idade na matrícula x evasão")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "eda_idade.png", dpi=150)
    plt.close(fig)

    # 5) Correlações com a evasão
    corr = df.drop(columns=[TARGET]).corrwith(y).sort_values()
    top = pd.concat([corr.head(8), corr.tail(8)])
    fig, ax = plt.subplots(figsize=(7, 5))
    top.plot.barh(ax=ax, color=["#54A24B" if v < 0 else "#E45756" for v in top])
    ax.set_title("Maiores correlações (Pearson) com evasão")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "eda_correlacao.png", dpi=150)
    plt.close(fig)

    # Estatísticas descritivas e qualidade dos dados
    df.describe().T.to_csv(REPORTS_DIR / "eda_estatisticas.csv")
    print("Formato:", df.shape)
    print("Valores ausentes:", int(df.isna().sum().sum()), "| Duplicados:", int(df.duplicated().sum()))
    print(df[TARGET].value_counts(normalize=True).round(3).to_string())
    print("\nTop correlações:\n", pd.concat([corr.head(5), corr.tail(5)]).round(3).to_string())


if __name__ == "__main__":
    main()
