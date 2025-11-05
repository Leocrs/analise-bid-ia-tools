#!/bin/bash

# Script de teste V2: Envia dados de teste REAIS e estruturados ao backend

echo "🚀 TESTE DE ANÁLISE COMPARATIVA V2"
echo "=================================="
echo ""

# Medir tempo
START=$(date +%s%N | cut -b1-13)

# Fazer requisição ao backend com dados TEST estruturados (SEM dependências externas)
echo "⏱️  Enviando análise com dados de teste estruturados..."
echo ""

# JSON com dados de teste bem estruturados
PAYLOAD=$(cat <<'EOF'
{
  "model": "gpt-5",
  "max_tokens": 4000,
  "messages": [
    {
      "role": "system",
      "content": "Você é um assistente de análise de orçamentos estruturado. Retorne SEMPRE as 6 seções em português: SEÇÃO 1 (FORNECEDORES), SEÇÃO 2 (TABELA HTML), SEÇÃO 3 (MIX), SEÇÃO 4 (COMERCIAL), SEÇÃO 5 (RANKING), SEÇÃO 6 (RECOMENDAÇÃO). Use nomes reais das empresas, não 'Fornecedor 1'."
    },
    {
      "role": "user",
      "content": "ANÁLISE COMPARATIVA DE 2 ORÇAMENTOS\n\n===== ORÇAMENTO 1: SR ALEXSON OBRA =====\nFornecedor: SR ALEXSON CONSTRUÇÃO LTDA\nCNPJ: 12.345.678/0001-50\nTelefone: (82) 98888-7777\nEmail: alexson@construcao.com.br\nEndereço: Rua das Obras, 150 - São Miguel dos Milagres - AL 57260-000\nContato: Sr. Alexson | Engenheiro de Obras\n\nOBRAS E MATERIAIS:\n- Concreto usinado: 50m³ x R$ 480,00 = R$ 24.000,00\n- Aço CA-50: 25 ton x R$ 3.800,00 = R$ 95.000,00\n- Aluguel de formas: 200m² x R$ 35,00 = R$ 7.000,00\n- Mão-de-obra (50 dias): 50 dias x R$ 1.200,00 = R$ 60.000,00\nTOTAL: R$ 186.000,00\n\nCondições Comerciais:\n- Desconto: 5% à vista\n- Pagamento: 50% entrada + 50% na conclusão\n- Prazo de entrega: Imediato (materiais) / 60 dias (obra)\n- Garantia: 24 meses (estrutura)\n- Validade: 30 dias\n\n===== ORÇAMENTO 2: BARRA DA PRAIA CONSTRUTORA =====\nFornecedor: BARRA DA PRAIA CONSTRUTORA LTDA\nCNPJ: 87.654.321/0001-99\nTelefone: (21) 99999-8888\nEmail: vendas@barrapraia.com.br\nEndereço: Av. Atlântica, 500 - Rio de Janeiro - RJ 20000-000\nContato: Maria Santos | Gerente de Projetos\n\nOBRAS E MATERIAIS:\n- Concreto usinado: 50m³ x R$ 520,00 = R$ 26.000,00\n- Aço CA-50: 25 ton x R$ 3.900,00 = R$ 97.500,00\n- Aluguel de formas: 200m² x R$ 40,00 = R$ 8.000,00\n- Mão-de-obra (50 dias): 50 dias x R$ 1.350,00 = R$ 67.500,00\nTOTAL: R$ 199.000,00\n\nCondições Comerciais:\n- Desconto: 3% à vista\n- Pagamento: 40% entrada + 60% em 30 dias\n- Prazo de entrega: Imediato (materiais) / 55 dias (obra)\n- Garantia: 36 meses (estrutura)\n- Validade: 45 dias\n\nGere a ANÁLISE COMPARATIVA integrada com todas as 6 seções."
    }
  ]
}
EOF
)

# Enviar para o backend
RESPONSE=$(curl -s -X POST https://analise-bid-ia-backend.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

END=$(date +%s%N | cut -b1-13)
TEMPO=$((($END - $START) / 1000))

echo "✅ Resposta recebida!"
echo ""
echo "⏱️  Tempo total: ${TEMPO}ms ($((TEMPO / 1000))s)"
echo ""

# Salvar resposta completa
echo "$RESPONSE" > /tmp/resposta_v2.json
echo "💾 Resposta salva em: /tmp/resposta_v2.json"
echo ""

# Mostrar resposta (truncada se muito grande)
echo "📊 RESULTADO:"
echo "================================"
if [ ${#RESPONSE} -gt 3000 ]; then
  echo "${RESPONSE:0:3000}"
  echo ""
  echo "... (resposta truncada - veja /tmp/resposta_v2.json para a resposta completa)"
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
  echo "❌ RESPOSTA VAZIA"
  exit 1
fi

# 3. Verificar presença de nomes reais (SR ALEXSON, BARRA DA PRAIA)
if echo "$RESPONSE" | grep -qi "alexson\|barra da praia\|sr\.\|maria santos"; then
  echo "✅ NOMES REAIS: Encontrados (fornecedores identificados)"
else
  echo "⚠️  NOMES REAIS: Não encontrados"
fi

# 4. Verificar se tem tabela HTML
if echo "$RESPONSE" | grep -q "<table\|<TR\|<tr"; then
  echo "✅ TABELA HTML: Encontrada"
else
  echo "⚠️  TABELA HTML: Não encontrada"
fi

# 5. Verificar se tem valores monetários
if echo "$RESPONSE" | grep -qi "r\$\|186.*000\|199.*000\|economia"; then
  echo "✅ VALORES MONETÁRIOS: Encontrados"
else
  echo "⚠️  VALORES MONETÁRIOS: Não encontrados"
fi

# 6. Verificar presença de SEÇÕES
echo ""
echo "Verificando presença de seções:"
for i in 1 2 3 4 5 6; do
  if echo "$RESPONSE" | grep -qi "seção $i\|SEÇÃO $i\|seçao $i\|seçoes"; then
    echo "  ✅ SEÇÃO $i ou referência a seções encontrada"
    break
  fi
done

# 7. Conta quantas vezes aparece análise
ANALISES=$(echo "$RESPONSE" | grep -io "seção\|ranking\|recomendação" | wc -l)
if [ $ANALISES -gt 10 ]; then
  echo "  ✅ Análise INTEGRADA: $ANALISES elementos de análise encontrados"
else
  echo "  ⚠️  Análise: $ANALISES elementos encontrados"
fi

# 8. Verificar se tem recomendação
if echo "$RESPONSE" | grep -qi "recomendação\|recomenda\|melhor\|escolh"; then
  echo "✅ RECOMENDAÇÃO: Encontrada"
else
  echo "⚠️  RECOMENDAÇÃO: Não encontrada"
fi

# 9. Validar estrutura (deve ter mais de 1000 caracteres de análise real)
RESPONSE_LEN=${#RESPONSE}
if [ $RESPONSE_LEN -gt 2000 ]; then
  echo "✅ CONTEÚDO: Análise completa ($RESPONSE_LEN caracteres)"
else
  echo "⚠️  CONTEÚDO: Resposta curta ($RESPONSE_LEN caracteres) - pode estar incompleta"
fi

echo ""
echo "================================"
echo "✨ Teste concluído!"
echo ""
echo "Para debug detalhado, veja: /tmp/resposta_v2.json"
