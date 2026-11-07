"""Funções de predição e explicabilidade (SHAP) reutilizadas pelo app e pelos scripts."""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
import shap

from .config import MODELS_DIR


def load_bundle(scenario: str) -> dict:
    return joblib.load(MODELS_DIR / f"model_{scenario}.joblib")


def _tree_explainer(bundle: dict) -> shap.TreeExplainer:
    return shap.TreeExplainer(bundle["model"].named_steps["clf"])


def shap_values_for(bundle: dict, X: pd.DataFrame) -> np.ndarray:
    """SHAP da classe 'Evasão' com formato (n_amostras, n_features), independente da versão do SHAP."""
    sv = _tree_explainer(bundle).shap_values(X[bundle["features"]])
    if isinstance(sv, list):  # versões antigas: lista [classe0, classe1]
        sv = sv[1]
    sv = np.asarray(sv)
    if sv.ndim == 3:  # (n, features, classes)
        sv = sv[:, :, 1]
    return sv


def predict_risk(bundle: dict, X: pd.DataFrame) -> pd.DataFrame:
    """Probabilidade de evasão e classificação de risco (usando o limiar calibrado para recall)."""
    proba = bundle["model"].predict_proba(X[bundle["features"]])[:, 1]
    thr = bundle["threshold"]
    level = np.where(proba >= max(thr + 0.25, 0.75), "Alto", np.where(proba >= thr, "Médio", "Baixo"))
    return pd.DataFrame({"prob_evasao": proba, "nivel_risco": level, "em_alerta": proba >= thr})


def explain_one(bundle: dict, row: pd.DataFrame, top_k: int = 6) -> pd.DataFrame:
    """Principais fatores (positivos = aumentam risco; negativos = reduzem) para um aluno."""
    sv = shap_values_for(bundle, row)[0]
    out = pd.DataFrame(
        {"fator": bundle["features"], "valor": row[bundle["features"]].iloc[0].values, "contribuicao": sv}
    )
    out["abs"] = out["contribuicao"].abs()
    return out.sort_values("abs", ascending=False).head(top_k).drop(columns="abs").reset_index(drop=True)
