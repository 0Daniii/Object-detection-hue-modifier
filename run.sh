#!/bin/bash

echo "============================================"
echo "      COLOR MORPH PRO - MACOS LAUNCHER"
echo "============================================"

# Verificăm dacă Python 3 este instalat
if ! command -v python3 &> /dev/null
then
    echo "[EROARE] Python 3 nu a fost găsit. Te rugăm să îl instalezi de pe python.org"
    exit
fi

echo "[1/2] Verificare și instalare biblioteci..."
# Pe Mac folosim de obicei python3 și pip3
pip3 install opencv-python numpy --quiet

if [ $? -ne 0 ]; then
    echo "[EROARE] Instalarea bibliotecilor a eșuat."
    exit
fi

echo "[2/2] Pornire aplicație..."
echo ""
python3 main.py

echo ""
echo "Aplicația a fost închisă."
