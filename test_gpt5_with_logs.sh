#!/bin/bash

# 🔍 Script para testar GPT-5 com logs detalhados
# Uso: bash test_gpt5_with_logs.sh

echo "=================================================="
echo "🔍 TESTE DE DIAGNÓSTICO GPT-5 COM LOGS"
echo "=================================================="
echo ""

BACKEND_URL="https://analise-bid-ia-backend.onrender.com"
DIAGNOSTIC_ENDPOINT="$BACKEND_URL/api/test-gpt5"

echo "📍 Endpoint: $DIAGNOSTIC_ENDPOINT"
echo "⏰ Horário: $(date)"
echo ""

# Teste 1: Teste simples
echo "🧪 Teste 1: Teste simples"
echo "Mensagem: 'Teste simples: responda OK'"
echo ""

curl -X POST "$DIAGNOSTIC_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Teste simples: responda OK"
  }' \
  -w "\n\n⏱️ Tempo total: %{time_total}s\n" 

echo ""
echo "=================================================="
echo ""

# Teste 2: Teste com prompt mais longo
echo "🧪 Teste 2: Teste com prompt mais longo"
echo "Mensagem: Multi-line prompt"
echo ""

curl -X POST "$DIAGNOSTIC_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Você é um assistente especializado em análise de documentos.\n\nAnalise o seguinte texto:\n\nO documento trata de análise de licitações públicas.\n\nQual é o assunto principal?"
  }' \
  -w "\n\n⏱️ Tempo total: %{time_total}s\n"

echo ""
echo "=================================================="
echo "✅ Testes concluídos!"
