@echo off

REM Prepare the virtual environment
if not exist ".venv" (
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    python -m playwright install
) else (
    call .venv\Scripts\activate.bat
)

REM Run command
set /p phone="Digite o numero do destinatario: "
set /p message="Digite a mensagem: "
python -u script.py +55%phone% "%message%"
pause