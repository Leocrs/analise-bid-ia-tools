#!/bin/bash

echo "🚀 === INICIANDO TOOLS ENGENHARIA - DOCUMENT AI ANALYZER ==="
echo "📅 Data: $(date)"
echo "🌍 Ambiente: Produção (Render)"
echo "============================================================"

# Verificar se a chave da OpenAI está configurada
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERRO: OPENAI_API_KEY não configurada!"
    exit 1
fi

echo "✅ OPENAI_API_KEY configurada"

# Iniciar aplicação com Gunicorn usando arquivo de configuração
echo "🔧 Iniciando Gunicorn com configurações otimizadas..."
exec gunicorn --config gunicorn.conf.py api.index:app