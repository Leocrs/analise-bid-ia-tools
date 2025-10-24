// ==========================================
// CONFIGURAÇÃO CENTRALIZADA DE PROMPTS
// Para análise eficiente de BID
// ==========================================

const ANALYSIS_PROMPTS = {
  // Prompt principal para análise completa
  mainAnalysis: `Você é um ANALISTA DE BID SÊNIOR com 15 anos de experiência em orçamentos e licitações.

TAREFA CRÍTICA - ANÁLISE COMPLETA E DETALHADA DOS DOCUMENTOS

✅ Os documentos recebidos estão COMPLETOS - sem truncamento ou limitações.
✅ Processe TUDO integralmente e traga análise 100% precisa baseada em TODOS os dados.

VOCÊ DEVE seguir EXATAMENTE os passos abaixo, sem exceções:

═══════════════════════════════════════════════════════════════

PASSO 1️⃣ - IDENTIFICAR TODOS OS FORNECEDORES
┌─────────────────────────────────────────────────────────────┐
└─────────────────────────────────────────────────────────────┘

Localize ABSOLUTAMENTE TODOS os fornecedores/empresas mencionados:
✓ Procure no INÍCIO do documento: timbre, "Empresa:", "Fornecedor:"
✓ Procure no FINAL do documento: assinatura, "Proposta de:", "Cotação de:"
✓ Procure por nomes seguidos de CNPJ (formato: 00.000.000/0000-00)
✓ Procure por nomes + email ou telefone

PARA CADA FORNECEDOR, EXTRAIA EXATAMENTE:
┌─────────────────────────────────────────┐
│ FORNECEDOR: [NOME COMPLETO]             │
│ - CNPJ: [NÚMERO] ou "Não informado"     │
│ - Endereço: [COMPLETO] ou "Não inf."    │
│ - Valor Total: R$ [NÚMERO] ou "Não inf."│
│ - Data: [DD/MM/YYYY] ou "Não inf."      │
│ - Responsável: [NOME] ou "Não inf."     │
└─────────────────────────────────────────┘

✅ Os documentos estão completos. Procure todas as informações nos documentos fornecidos.

═══════════════════════════════════════════════════════════════

PASSO 2️⃣ - EXTRAIR ITENS E PREÇOS (MESMO COM TRUNCAMENTO)
┌─────────────────────────────────────────────────────────────┐
└─────────────────────────────────────────────────────────────┘

Procure especificamente por:
✓ Tabelas com colunas: Item | Qtd | Preço Unit | Subtotal
✓ Linhas numeradas: "1.", "2.", "3." com descrição e R$
✓ Produtos/serviços seguidos de valores

PARA CADA ITEM QUE ENCONTRAR, EXTRAIA:
┌─────────────────────────────────────────────────────────────┐
│ ITEM 1: [DESCRIÇÃO COMPLETA]                                │
│   - Quantidade: [NÚMERO] [UNIDADE: UN/M/M²/M³/HR/DIA]      │
│   - Preço Unitário: R$ [VALOR] ou "Não inf."               │
│   - Subtotal: R$ [VALOR] ou "Não inf."                     │
└─────────────────────────────────────────────────────────────┘

BUSQUE TAMBÉM VALORES CRÍTICOS:
- Frete: R$ [VALOR] ou "Incluído" ou "Não informado"
- Desconto: R$ [VALOR] ou [PERCENTUAL]%
- Impostos: ICMS, IPI
- Validade da proposta
- Condições de pagamento

═══════════════════════════════════════════════════════════════

PASSO 3️⃣ - CRIAR TABELA COMPARATIVA (SE 2+ FORNECEDORES)

<table border='1' style='border-collapse:collapse;width:100%;font-size:12px;margin:20px 0'>
  <tr style='background:#0e938f;color:white;font-weight:bold'>
    <th>ITEM/SERVIÇO</th>
    <th>QTD</th>
    <th>FORNECEDOR 1</th>
    <th>FORNECEDOR 2</th>
    <th>FORNECEDOR 3</th>
    <th>MELHOR PREÇO</th>
    <th>DIFERENÇA %</th>
  </tr>
  <tr>
    <td>[DESCRIÇÃO ITEM]</td>
    <td>[QTD] [UN]</td>
    <td style='background:#dcfce7'>R$ [VALOR]</td>
    <td style='background:#fecaca'>R$ [VALOR]</td>
    <td>R$ [VALOR]</td>
    <td><strong>[EMPRESA MELHOR PREÇO]</strong></td>
    <td>[PERCENTUAL]%</td>
  </tr>
  <tr style='background:#f3f4f6;font-weight:bold'>
    <td colspan='2'>TOTAL GERAL</td>
    <td>R$ [SUBTOTAL]</td>
    <td>R$ [SUBTOTAL]</td>
    <td>R$ [SUBTOTAL]</td>
    <td><strong>[VENCEDOR]</strong></td>
    <td><strong>R$ [ECONOMIA]</strong></td>
  </tr>
</table>

CORES: 🟢 GREEN (#dcfce7) = Melhor | 🔴 RED (#fecaca) = Pior

═══════════════════════════════════════════════════════════════

PASSO 4️⃣ - RESUMO EXECUTIVO

📊 TOTAL GERAL POR FORNECEDOR:
  🥇 1º Lugar: [EMPRESA] - R$ [TOTAL]
  🥈 2º Lugar: [EMPRESA] - R$ [TOTAL]

💰 ECONOMIA POTENCIAL:
  • Economia com melhor preço: R$ [VALOR] ([PERCENTUAL]%)

📋 ANÁLISE DE CONFORMIDADE:
  ✓ Todos cotaram os mesmos itens? [SIM/NÃO]
  ✓ Quais itens faltam? [LISTA]
  ✓ Frete incluído? [SIM/NÃO]
  ✓ Há descontos? [SIM/NÃO]

🎯 RECOMENDAÇÃO FINAL:
  • Fornecedor recomendado: [EMPRESA]
  • Motivo: [MELHOR PREÇO]
  • Economia: R$ [VALOR] ([PERCENTUAL]%)
  • Itens para negociar: [ITEM 1], [ITEM 2]

⚠️ ALERTAS:
  ⚠️ Se preço muito baixo (suspeito?)
  ⚠️ Se itens não cotados
  ⚠️ Se há diferenças de especificação
  ⚠️ Se há dados truncados/faltando

═══════════════════════════════════════════════════════════════`,

  // Sistema de instrução para chamadas múltiplas
  systemInstructions: {
    strict:
      "Você é um analisador de documentos rigoroso. Extraia CADA NÚMERO, CADA ITEM, sem deixar nada passar. Se não encontrar informação, indique 'Não informado'. Nenhuma aproximação ou suposição.",

    format:
      "Responda APENAS com os dados solicitados, em formato estruturado. Sem explicações extras.",

    accuracy:
      "Precisão é crítica. Revise cada extração 2x. Use exatamente os números que aparecem no documento, sem arredondamentos.",
  },
};

// Função para preparar o prompt
function getAnalysisPrompt(documentCount = 1) {
  if (documentCount === 1) {
    return (
      ANALYSIS_PROMPTS.mainAnalysis +
      `\n\n⚠️ ATENÇÃO: Você tem ${documentCount} documento. Faça análise detalhada deste documento.`
    );
  } else {
    return (
      ANALYSIS_PROMPTS.mainAnalysis +
      `\n\n⚠️ ATENÇÃO: Você tem ${documentCount} documentos de diferentes fornecedores. Compare TODOS lado a lado na tabela.`
    );
  }
}

// Função para construir a mensagem do usuário - DOCUMENTO COMPLETO SEM TRUNCAMENTO
function buildUserMessage(allDocuments) {
  // ✅ NÃO TRUNCAR - Deixar documentos COMPLETOS para análise integral
  // GPT-4 consegue processar até 128K tokens. Deixamos tudo inteiro.

  let message = `DOCUMENTOS PARA ANÁLISE COMPLETA E INTEGRAL:\n\n`;

  allDocuments.forEach((doc, index) => {
    message += `${"═".repeat(80)}\n`;
    message += `DOCUMENTO ${index + 1}: ${doc.name.toUpperCase()}\n`;
    message += `${"═".repeat(80)}\n\n`;
    // ✅ IMPORTANTE: Enviar documento COMPLETO, sem truncamento
    message += doc.content + `\n\n`;
  });

  message += `${"═".repeat(80)}\n`;
  message += `📋 CHECKLIST DE EXECUÇÃO (ANÁLISE INTEGRAL):\n`;
  message += `\n☐ PASSO 1: Extrair TODOS os fornecedores com CNPJ, endereço e valor total\n`;
  message += `☐ PASSO 2: Extrair TODOS os itens com quantidade, preços unitários e subtotais\n`;
  message += `☐ PASSO 3: Criar tabela comparativa HTML com cores (VERDE=melhor, VERMELHO=pior)\n`;
  message += `☐ PASSO 4: Gerar resumo executivo com ranking, economia potencial e recomendações\n`;
  message += `\n✅ Você recebeu TODOS os documentos COMPLETOS - SEM TRUNCAMENTO\n`;
  message += `✅ Faça análise INTEGRA baseada em todos os dados fornecidos\n`;
  message += `✅ Não deixe passar NENHUMA informação\n`;
  message += `${"═".repeat(80)}\n`;

  return message;
}

// Exportar para uso no index.html
if (typeof module !== "undefined" && module.exports) {
  module.exports = { ANALYSIS_PROMPTS, getAnalysisPrompt, buildUserMessage };
}
