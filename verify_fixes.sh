#!/bin/bash
# Script para verificar se todas as correções foram aplicadas

echo "🔍 Verificando correções implementadas..."
echo ""

# Cor verde
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

check_fix() {
    local file="$1"
    local pattern="$2"
    local name="$3"
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $name"
        return 0
    else
        echo -e "${RED}✗${NC} $name"
        return 1
    fi
}

echo "📄 Frontend (index.html):"
check_fix "analise-bid-ia-tools/index.html" 'String(data.modelo' "localStorage salva como String"
check_fix "analise-bid-ia-tools/index.html" 'if .*!systemPrompt.*trim' "Validação de systemPrompt"
check_fix "analise-bid-ia-tools/index.html" 'if .*!userMessage.*trim' "Validação de userMessage"
check_fix "analise-bid-ia-tools/index.html" 'if .*!content.*trim' "Validação de content vazios"
check_fix "analise-bid-ia-tools/index.html" 'typeof dados.*===.*string' "Validação de tipos no localStorage"

echo ""
echo "🐍 Backend (api/index.py):"
check_fix "analise-bid-ia-tools/api/index.py" 'retry_attempt=1' "Retry com parâmetro de tentativa"
check_fix "analise-bid-ia-tools/api/index.py" 'time.sleep.2' "Backoff de 2 segundos"
check_fix "analise-bid-ia-tools/api/index.py" 'msg_content\[:50\]' "Preview de conteúdo em logs"
check_fix "analise-bid-ia-tools/api/index.py" 'not msg.get.*content.*strip' "Validação de mensagens vazias"

echo ""
echo "📚 Documentação:"
check_fix "analise-bid-ia-tools/DEBUG_FIXES.md" "Correções de Debug" "Arquivo de debug criado"

echo ""
echo "✅ Verificação completa!"
echo ""
echo "📋 Próximos passos:"
echo "1. Commit e push das mudanças"
echo "2. Redeploy no Render.com"
echo "3. Limpar localStorage (opcional):"
echo "   localStorage.clear() no DevTools Console"
echo "4. Testar com novos documentos"
