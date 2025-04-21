@echo off
REM Cria ambiente virtual se não existir
if not exist venv (
    python -m venv venv
)
REM Ativa o ambiente virtual
call venv\Scripts\activate

REM Instala dependências
pip install -r requirements.txt

REM Copia .env.example para .env se não existir
if not exist .env (
    copy .env.example .env
    echo Copie suas credenciais para o arquivo .env
)

echo Ambiente pronto! Para rodar o projeto:
echo.
echo     call venv\Scripts\activate
echo     python src\main.py
