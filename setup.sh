#!/bin/bash

echo "🚀 Creando entorno virtual (.venv)..."
python3 -m venv .venv

echo "🔄 Activando el entorno..."
source .venv/bin/activate

echo "📦 Actualizando pip..."
pip install --upgrade pip

echo "📥 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

echo "✅ ¡Entorno listo y dependencias instaladas!"