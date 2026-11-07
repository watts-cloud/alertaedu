"""Carga e preparação dos dados (UCI: Predict Students' Dropout and Academic Success).

Fonte: Realinho, Machado, Baptista e Martins (2021), UCI Machine Learning Repository,
https://doi.org/10.24432/C5MC89 (CC BY 4.0). Artigo: Data 7(11):146, 2022,
https://doi.org/10.3390/data7110146. Referências completas em docs/referencias.md.
"""
from __future__ import annotations

import pandas as pd

from .config import DATA_DIR, DATA_FILE, SEM1, SEM2, TARGET


def download_dataset(force: bool = False) -> pd.DataFrame:
    """Baixa o dataset do UCI (id=697) e salva em data/. Reutiliza o CSV local se existir."""
    if DATA_FILE.exists() and not force:
        return pd.read_csv(DATA_FILE)

    from ucimlrepo import fetch_ucirepo

    ds = fetch_ucirepo(id=697)
    df = pd.concat([ds.data.features, ds.data.targets], axis=1)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_FILE, index=False)
    # Dicionário de variáveis (metadados oficiais) para a documentação
    ds.variables.to_csv(DATA_DIR / "dicionario_de_variaveis.csv", index=False)
    return df


def load_data() -> pd.DataFrame:
    df = download_dataset()
    df.columns = [c.strip() for c in df.columns]
    return df


def make_binary_target(df: pd.DataFrame) -> pd.Series:
    """1 = Dropout (evasão); 0 = Enrolled ou Graduate."""
    return (df[TARGET] == "Dropout").astype(int)


def columns_for_scenario(df: pd.DataFrame, scenario: str) -> list[str]:
    """Seleciona as colunas disponíveis em cada momento do alerta."""
    features = [c for c in df.columns if c != TARGET]
    if scenario == "A_matricula":
        return [c for c in features if not c.startswith((SEM1, SEM2))]
    if scenario == "B_1_semestre":
        return [c for c in features if not c.startswith(SEM2)]
    if scenario == "C_2_semestre":
        return features
    raise ValueError(f"Cenário desconhecido: {scenario}")
