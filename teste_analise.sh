#!/bin/bash

# Script de teste: Envia 2 PDFs reais ao backend e mede o tempo

echo "🚀 TESTE DE ANÁLISE COMPARATIVA"
echo "================================"
echo ""

# Encontrar PDFs reais
PDF1=$(find /c/Users/TOOLS-96/Github -name "*SR ALEXSON*" -o -name "*ALEXSON*" 2>/dev/null | head -1)
PDF2=$(find /c/Users/TOOLS-96/Github -name "*BarDaPraia*" 2>/dev/null | head -1)

if [ -z "$PDF1" ] || [ -z "$PDF2" ]; then
  echo "❌ ERRO: PDFs não encontrados"
  echo "Procurando em: /c/Users/TOOLS-96/Github"
  find /c/Users/TOOLS-96/Github -name "*.pdf" 2>/dev/null | head -5
  exit 1
fi

echo "📄 PDFs a testar:"
echo "  1. $(basename "$PDF1") ($(du -h "$PDF1" | cut -f1))"
echo "  2. $(basename "$PDF2") ($(du -h "$PDF2" | cut -f1))"
echo ""

# Extrair conteúdo dos PDFs (usando strings para ler texto dos PDFs)
echo "📖 Extraindo conteúdo dos PDFs..."
CONTENT1=$(strings "$PDF1" 2>/dev/null | head -2000 | tr '\n' ' ')
CONTENT2=$(strings "$PDF2" 2>/dev/null | head -2000 | tr '\n' ' ')

# Pegar apenas 8000 caracteres de cada
CONTENT1=${CONTENT1:0:8000}
CONTENT2=${CONTENT2:0:8000}

echo "  ✅ PDF 1: ${#CONTENT1} caracteres extraídos"
echo "  ✅ PDF 2: ${#CONTENT2} caracteres extraídos"
echo ""

# Medir tempo
START=$(date +%s%N | cut -b1-13)

# Fazer requisição ao backend com dados REAIS
echo "⏱️  Enviando análise (medindo tempo)..."
echo ""

RESPONSE=$(curl -s -X POST https://analise-bid-ia-backend.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  --data @- <<EOF
{
  "model": "gpt-5",
  "max_tokens": 4000,
  "messages": [
    {
      "role": "system",
      "content": "ANÁLISE COMPARATIVA DE ORÇAMENTOS - SEÇÕES 1-6\n\nVocê receberá conteúdo de múltiplos orçamentos. Gere:\n\nSEÇÃO 1️⃣: FORNECEDORES (lista simples: Nome | CNPJ | Tel | Email | Contato)\nSEÇÃO 2️⃣: TABELA COMPARATIVA HTML (com cores: verde=menor, vermelho=maior)\nSEÇÃO 3️⃣: MIX DE PREÇO (itens onde cada fornecedor é mais barato)\nSEÇÃO 4️⃣: COMERCIAL (descontos, prazos, garantias por fornecedor)\nSEÇÃO 5️⃣: RANKING (1º, 2º lugar com valores)\nSEÇÃO 6️⃣: RECOMENDAÇÃO (qual contratar e por quê)\n\nRegras: Verde (#dcfce7)=melhor | Vermelho (#fecaca)=pior | Nomes reais, não 'Forn.1' | Extrai TODOS os itens | Se não encontrar: 'Não informado'"
    },
    {
      "role": "user",
      "content": "Analise estes 2 orçamentos e gere uma ÚNICA análise comparativa integrada com todas as 6 seções.\n\nARQUIVO 1: $(basename "$PDF1")\n\n$CONTENT1\n\nARQUIVO 2: $(basename "$PDF2")\n\n$CONTENT2\n\nGere tabela HTML comparativa com todos os itens de ambos os fornecedores."
    }
  ]
}
EOF
)

END=$(date +%s%N | cut -b1-13)
TEMPO=$((($END - $START) / 1000))

echo "✅ Resposta recebida!"
echo ""
echo "⏱️  Tempo total: ${TEMPO}ms ($((TEMPO / 1000))s)"
echo ""
echo "📊 RESULTADO:"
echo "================================"

# Salvar resposta em arquivo para debug
echo "$RESPONSE" > /tmp/resposta_analise.json
echo "💾 Resposta salva em: /tmp/resposta_analise.json"
echo ""

# Mostrar resposta (truncada se muito grande)
if [ ${#RESPONSE} -gt 2000 ]; then
  echo "${RESPONSE:0:2000}"
  echo ""
  echo "... (resposta truncada, veja arquivo completo em /tmp/resposta_analise.json)"
else
  echo "$RESPONSE"
fi

echo ""
echo "================================"
echo ""

# VALIDAÇÕES
echo "🔍 VALIDAÇÕES:"
echo ""

# 1. Verificar tempo
if [ $TEMPO -lt 15000 ]; then
  echo "✅ TEMPO: OK (<15s) - ${TEMPO}ms"
else
  echo "❌ TEMPO: LENTO (>15s) - ${TEMPO}ms"
fi

# 2. Verificar se tem conteúdo
if [ -z "$RESPONSE" ]; then
  echo "❌ RESPOSTA VAZIA - Nenhum conteúdo retornado"
  exit 1
fi

# 3. Verificar se tem as 6 seções (grep direto na resposta)
echo ""
echo "Verificando seções:"

for i in 1 2 3 4 5 6; do
  if echo "$RESPONSE" | grep -qi "seção $i\|SEÇÃO $i\|seção.?$i\|$i\)"; then
    echo "  ✅ SEÇÃO $i: Encontrada"
  else
    echo "  ❌ SEÇÃO $i: NÃO encontrada"
  fi
done

# 4. Verificar se tem tabela HTML
if echo "$RESPONSE" | grep -q "<table\|<TR\|<tr"; then
  echo "  ✅ TABELA HTML: Encontrada"
else
  echo "  ⚠️  TABELA HTML: NÃO encontrada (pode estar em formato diferente)"
fi

# 5. Verificar se tem dados de fornecedor (CNPJ ou razão social)
if echo "$RESPONSE" | grep -qi "cnpj\|razão social\|empresa\|fornecedor"; then
  echo "  ✅ DADOS DE FORNECEDOR: Encontrados"
else
  echo "  ⚠️  DADOS DE FORNECEDOR: NÃO encontrados"
fi

# 6. Verificar se é análise única (não duplicada)
REPETICOES=$(echo "$RESPONSE" | grep -io "seção 1" | wc -l)
if [ $REPETICOES -eq 1 ] || [ $REPETICOES -lt 3 ]; then
  echo "  ✅ ANÁLISE ÚNICA: OK ($REPETICOES menção de SEÇÃO 1)"
elif [ $REPETICOES -gt 3 ]; then
  echo "  ❌ ANÁLISE DUPLICADA: $REPETICOES repetições de SEÇÃO 1"
else
  echo "  ⚠️  ANÁLISE: $REPETICOES menção de SEÇÃO 1"
fi

echo ""
echo "================================"
echo "✨ Teste concluído!"
