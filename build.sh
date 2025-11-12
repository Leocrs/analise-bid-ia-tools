#!/bin/bash

echo "🔨 === BUILD SCRIPT - TOOLS ENGENHARIA ==="
echo "📅 $(date)"
echo "=========================================="

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Tornar o script de start executável
echo "🔧 Configurando permissões..."

echo "✅ Build concluído com sucesso!"
echo "🚀 Pronto para deploy!"