"""Configurações centrais do projeto AlertaEdu."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
FIG_DIR = REPORTS_DIR / "figures"
DATA_FILE = DATA_DIR / "students_dropout.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.2
TARGET = "Target"

# Cenários de "antecedência do alerta": quais colunas estão disponíveis em cada momento.
# A: no ato da matrícula (sem nenhuma nota)
# B: ao final do 1º semestre
# C: ao final do 2º semestre (maior acurácia, mas alerta mais tardio)
SEM1 = "Curricular units 1st sem"
SEM2 = "Curricular units 2nd sem"

SCENARIOS = {
    "A_matricula": "No ato da matrícula (sem notas)",
    "B_1_semestre": "Fim do 1º semestre",
    "C_2_semestre": "Fim do 2º semestre",
}

# Atributos sensíveis usados apenas na auditoria de justiça (nunca como regra de decisão).
SENSITIVE = {
    "Gender": {0: "Feminino", 1: "Masculino"},
    "Scholarship holder": {0: "Não bolsista", 1: "Bolsista"},
    "Debtor": {0: "Não devedor", 1: "Devedor"},
}
