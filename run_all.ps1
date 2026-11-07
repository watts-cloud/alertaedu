$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path .venv)) { py -3 -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -q -r requirements.txt

.\.venv\Scripts\python.exe -m src.eda
.\.venv\Scripts\python.exe -m src.train
.\.venv\Scripts\python.exe -m src.explain

Write-Host "`nPipeline concluído. Abrindo o app..."
.\.venv\Scripts\python.exe -m streamlit run app/app.py
