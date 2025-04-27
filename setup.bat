@echo off
REM Create virtual environment if it doesn't exist
if not exist venv (
    python -m venv venv
)
REM Activate the virtual environment
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Copy .env.example to .env if it doesn't exist
if not exist .env (
    copy .env.example .env
    echo Copy your credentials to the .env file
)

echo Environment ready! To run the project:
echo.
echo     call venv\Scripts\activate
echo     python src\main.py
