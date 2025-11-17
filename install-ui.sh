#!/bin/bash
# Script de instalación para la UI de deployment

echo "🔧 Instalando dependencias para la UI..."
pip3 install -r requirements.txt

echo ""
echo "✅ Instalación completada!"
echo ""
echo "Para ejecutar la interfaz:"
echo "   python3 deploy-config-ui.py"
