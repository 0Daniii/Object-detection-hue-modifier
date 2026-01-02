@echo off
title Color Morph Pro - Auto Launcher
echo ============================================
echo      COLOR MORPH PRO - AUTO LAUNCHER
echo ============================================
echo.

:: Verificam daca Python este instalat
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [EROARE] Python nu a fost gasit! Te rugam sa instalezi Python si sa bifezi "Add to PATH".
    pause
    exit
)

echo [1/2] Verificare si instalare biblioteci...
pip install opencv-python numpy --quiet

if %errorlevel% neq 0 (
    echo [EROARE] Instalarea bibliotecilor a esuat. Verifica conexiunea la internet.
    pause
    exit
)

echo [2/2] Pornire aplicatie...
echo.
:: Inlocuieste "main.py" cu numele exact al fisierului tau daca e diferit
python main.py

echo.
echo Aplicatia a fost inchisa.
pause
