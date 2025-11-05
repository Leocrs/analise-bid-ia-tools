#!/bin/bash

echo "================================"
echo "🚀 DEPLOY - TOOLS ENGENHARIA"
echo "================================"
echo ""

# Passo 1: Verificar Status
echo "📊 Verificando status do Git..."
git status
echo ""

# Passo 2: Adicionar Todas as Mudanças
echo "📝 Adicionando arquivos modificados..."
git add .
echo "✅ Arquivos adicionados"
echo ""

# Passo 3: Commit com Mensagem
echo "💬 Criando commit..."
git commit -m "feat: sincronização de configurações GPT-5 com backend - 8000 tokens"
echo ""

# Passo 4: Push para GitHub
echo "🌐 Enviando para GitHub..."
git push origin main
echo ""

# Passo 5: Confirmação
echo "================================"
echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "================================"
echo ""
echo "📌 Próximos passos:"
echo "1. Vercel: Deploy automático em 1-2 minutos"
echo "2. Render: Deploy automático em 2-3 minutos"
echo "3. Teste em outro PC/navegador"
echo ""
