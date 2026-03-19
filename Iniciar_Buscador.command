#!/bin/bash
cd "$(dirname "$0")"

VENV_PATH="$HOME/.app_venv_buscador"

if [ ! -d "$VENV_PATH" ]; then
    echo "=================================================="
    echo "📦 Creando entorno virtual local seguro..."
    echo "   (Fuera de Google Drive para evitar congelamientos)"
    echo "=================================================="
    python3 -m venv "$VENV_PATH"
    
    echo "Descargando e instando librerías necesarias... (Tomará un minuto)"
    "$VENV_PATH/bin/pip" install -r requirements.txt
fi

echo "=================================================="
echo "🚀 ¡El servidor local ya está encendido y trabajando!"
echo "   La consola se quedará 'fija' aquí (es normal)."
echo "   Abre tu navegador en: http://localhost:8501"
echo "=================================================="

# Ejecutar streamlit desde el entorno local
"$VENV_PATH/bin/streamlit" run app.py

