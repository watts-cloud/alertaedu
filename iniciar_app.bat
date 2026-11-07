@echo off
chcp 65001 >nul
title AlertaEdu - Aplicativo Streamlit
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

echo ========================================================
echo   AlertaEdu - Identificacao Precoce de Risco de Evasao
echo ========================================================
echo.

REM 1. Se .venv ja existe e possui o Streamlit instalado, abre direto
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import streamlit" >nul 2>&1
    if not errorlevel 1 goto CHECK_MODELS
)

echo [1/2] Preparando ambiente virtual Python (.venv)...
set "PY_CMD="
py -3.13 -c "import sys" >nul 2>&1 && set "PY_CMD=py -3.13"
if not defined PY_CMD (py -3.12 -c "import sys" >nul 2>&1 && set "PY_CMD=py -3.12")
if not defined PY_CMD (py -3.11 -c "import sys" >nul 2>&1 && set "PY_CMD=py -3.11")
if not defined PY_CMD (py -3 -c "import sys" >nul 2>&1 && set "PY_CMD=py -3")
if not defined PY_CMD (python -c "import sys" >nul 2>&1 && set "PY_CMD=python")

if not defined PY_CMD (
    echo [ERRO] Python 3.11+ nao encontrado neste computador.
    echo Baixe em https://www.python.org/downloads/ marcando "Add python.exe to PATH".
    pause
    exit /b 1
)

%PY_CMD% -m venv .venv
if not exist ".venv\Scripts\python.exe" (
    echo [ERRO] Falha ao criar a pasta .venv usando "%PY_CMD%".
    pause
    exit /b 1
)

echo [2/2] Instalando dependencias (aguarde 1 a 2 minutos na primeira vez)...
".venv\Scripts\python.exe" -m pip install --upgrade pip -q
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar pacotes do requirements.txt.
    pause
    exit /b 1
)

:CHECK_MODELS
if not exist "models\model_B_1_semestre.joblib" (
    echo Modelos nao encontrados. Executando treinamento inicial...
    ".venv\Scripts\python.exe" -m src.train
    ".venv\Scripts\python.exe" -m src.explain
)

echo Abrindo o AlertaEdu no navegador (http://localhost:8501)...
echo Para encerrar o servidor, pressione Ctrl+C nesta janela ou feche-a.
echo.
".venv\Scripts\python.exe" -m streamlit run app/app.py --browser.gatherUsageStats false %*
if errorlevel 1 pause