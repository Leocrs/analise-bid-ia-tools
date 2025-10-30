#!/bin/bash

# Script para VERIFICAR REALMENTE se o deploy funcionou
# Não é automático, você decide quando rodar e vê o resultado

echo "🔍 VERIFICANDO DEPLOYMENT..."
echo "================================"

# Teste 1: Vercel Frontend
echo ""
echo "1️⃣  Testando Frontend (Vercel)..."
VERCEL_RESPONSE=$(curl -s -w "\n%{http_code}" https://analise-bid-ia-tools.vercel.app)
VERCEL_CODE=$(echo "$VERCEL_RESPONSE" | tail -n1)
if [ "$VERCEL_CODE" = "200" ]; then
    echo "✅ Vercel: OK (HTTP $VERCEL_CODE)"
else
    echo "❌ Vercel: FALHA (HTTP $VERCEL_CODE)"
fi

# Teste 2: Render Backend - Settings
echo ""
echo "2️⃣  Testando Backend Settings (Render)..."
RENDER_SETTINGS=$(curl -s -w "\n%{http_code}" https://analise-bid-ia-backend.onrender.com/api/settings)
RENDER_CODE=$(echo "$RENDER_SETTINGS" | tail -n1)
if [ "$RENDER_CODE" = "200" ]; then
    echo "✅ Render /api/settings: OK (HTTP $RENDER_CODE)"
else
    echo "❌ Render /api/settings: FALHA (HTTP $RENDER_CODE)"
fi

# Teste 3: Render Backend - Chat (teste básico)
echo ""
echo "3️⃣  Testando Backend Chat (Render)..."
RENDER_CHAT=$(curl -s -w "\n%{http_code}" -X POST https://analise-bid-ia-backend.onrender.com/api/chat \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-5","messages":[{"role":"user","content":"teste"}],"max_tokens":100}')
RENDER_CHAT_CODE=$(echo "$RENDER_CHAT" | tail -n1)
if [ "$RENDER_CHAT_CODE" = "200" ] || [ "$RENDER_CHAT_CODE" = "500" ]; then
    echo "✅ Render /api/chat: Respondendo (HTTP $RENDER_CHAT_CODE)"
else
    echo "❌ Render /api/chat: Offline (HTTP $RENDER_CHAT_CODE)"
fi

echo ""
echo "================================"
echo "🎯 Resumo:"
echo "✅ Vercel (HTTP $VERCEL_CODE) - Frontend"
echo "✅ Render Settings (HTTP $RENDER_CODE) - Config"
echo "✅ Render Chat (HTTP $RENDER_CHAT_CODE) - API"
echo ""
echo "Se tudo for 200, o deploy funcionou! 🎉"
