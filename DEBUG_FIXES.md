# 🔧 Correções de Debug - Console Errors

## Problemas Identificados e Soluções

### 1. ❌ `SyntaxError: "[object Object]" is not valid JSON`

**Problema:** Extensão do Edge (content.js) tentava fazer `JSON.parse()` em objetos ao invés de strings JSON válidas.

**Causa Raiz:** Linhas 503-505 do `index.html` salvavam dados no localStorage sem conversão para string:

```javascript
// ❌ ERRADO - Salvava objeto/número direto
localStorage.setItem("openai_model", data.modelo); // data.modelo é string OK
localStorage.setItem("max_tokens", data.max_tokens); // ⚠️ Número! Causa erro
localStorage.setItem("chunk_size", data.chunk_size); // ⚠️ Número! Causa erro
```

**Solução:** Converter para string explicitamente:

```javascript
// ✅ CORRETO - Sempre usar String()
localStorage.setItem("openai_model", String(data.modelo || "gpt-5"));
localStorage.setItem("max_tokens", String(data.max_tokens || 4000));
localStorage.setItem("chunk_size", String(data.chunk_size || 8000));
```

---

### 2. ❌ `Unchecked runtime.lastError: The message port closed before a response was received`

**Problema:** Comunicação entre abas/extensão quebrada.

**Causa:** Causado pelos erros de JSON parsing acima, que travavam o runtime.

**Solução:** Fixa-se corrigindo os erros de JSON, além de adicionar validação robusta em `carregarBaseHistorica()`.

---

### 3. ❌ `POST https://analise-bid-ia-backend.onrender.com/api/chat 500 (Internal Server Error)`

**Problema:** `"OpenAI retornou resposta vazia mesmo após tentativas - tente novamente"`

**Causa Raiz:**

- Backend recebe requisição com mensagens vazias ou inválidas
- OpenAI retorna resposta vazia (possíveis causas: timeout, documentos corrompidos, limite de tokens)
- Backend retorna 500 ao invés de tentar recuperar

**Soluções Implementadas:**

#### A. Validação no Frontend (`index.html`)

```javascript
// ✅ Novo: Validar mensagens antes de enviar
if (!systemPrompt || !systemPrompt.trim()) {
  throw new Error("❌ Erro: System prompt está vazio");
}
if (!userMessage || !userMessage.trim()) {
  throw new Error("❌ Erro: Mensagem do usuário está vazia");
}
```

#### B. Melhor Tratamento de Erros no Frontend

```javascript
// ✅ Novo: Tratamento robusto de erros da API
if (!content || !content.trim()) {
  throw new Error(
    "Backend retornou conteúdo vazio. Tente novamente com documentos menores."
  );
}
```

#### C. Retry Inteligente no Backend (`api/index.py`)

```python
# ✅ Novo: Múltiplas tentativas com backoff
retry_count = 0
max_retries = 2
while retry_count < max_retries and (not content or not content.strip()):
    retry_count += 1
    time.sleep(2)  # Aguardar antes de retry
    response2, error2 = process_openai_request(messages, model, max_tokens, retry_attempt=retry_count+1)
    # ... verificar resposta ...
```

#### D. Melhor Logging em `process_openai_request()`

```python
# ✅ Novo: Validação de mensagens antes de enviar
for msg in messages:
    if not msg.get('content') or not msg.get('content').strip():
        log_debug(f"❌ ERRO: Mensagem de role '{msg.get('role')}' está vazia!")
        raise ValueError(f"Mensagem de role '{msg.get('role')}' está vazia")

# ✅ Novo: Preview do conteúdo
content_preview = msg_content[:50] + "..." if len(msg_content) > 50 else msg_content
log_debug(f"   • Mensagem {idx+1} ({msg_role}): {len(msg_content)} chars - {repr(content_preview)}")
```

---

### 4. ✅ `Unchecked runtime.lastError: The message port closed` (Validação localStorage)

**Problema:** `carregarBaseHistorica()` não validava dados do localStorage.

**Solução:** Adicionar try-catch e validação:

```javascript
function carregarBaseHistorica() {
  try {
    const dados = localStorage.getItem("toolsBaseHistorica");
    if (dados) {
      // ✅ Validar se é string JSON válida antes de fazer parse
      if (typeof dados === "string" && dados.startsWith("[")) {
        baseHistorica = JSON.parse(dados);
      } else if (typeof dados === "object") {
        baseHistorica = dados;
      } else {
        console.warn("⚠️ Dados inválidos no localStorage, limpando...");
        localStorage.removeItem("toolsBaseHistorica");
        baseHistorica = [];
      }
    }
  } catch (error) {
    console.error("❌ Erro ao carregar base histórica:", error);
    localStorage.removeItem("toolsBaseHistorica");
    baseHistorica = [];
  }
}
```

---

## 📋 Checklist de Verificação

- [x] localStorage sempre usa `String()` para converter valores
- [x] Validação de mensagens vazias no frontend
- [x] Validação de conteúdo vazio na resposta
- [x] Retry inteligente no backend (até 2 tentativas)
- [x] Backoff de 2 segundos entre retries
- [x] Melhor logging em todas as etapas
- [x] Proteção contra JSON parsing de objetos
- [x] Mensagens de erro mais descritivas

---

## 🧪 Como Testar

1. **Teste localStorage:**

   ```javascript
   // Abra o DevTools e execute:
   localStorage.getItem("openai_model"); // Deve ser string "gpt-5"
   localStorage.getItem("max_tokens"); // Deve ser string "4000"
   ```

2. **Teste base histórica:**

   ```javascript
   localStorage.getItem("toolsBaseHistorica"); // Deve ser JSON array
   // Limpar se necessário:
   localStorage.removeItem("toolsBaseHistorica");
   ```

3. **Teste envio de documentos:**

   - Envie um documento PDF/XLSX
   - Verifique no DevTools console os logs de validação
   - Verifique na aba Network a resposta da API

4. **Monitore os logs:**
   - Backend: `app_debug.log` (Render.com)
   - Frontend: DevTools Console (F12)

---

## 🚀 Próximos Passos Recomendados

1. **Aumentar timeout do OpenAI** se ainda houver timeouts (linha 103 em `api/index.py`)
2. **Implementar circuit breaker** para evitar sobrecarga
3. **Adicionar métricas** de sucesso/falha de chamadas
4. **Considerar comprimir documentos** antes de enviar se forem muito grandes
5. **Implementar fila de processamento** para requisições em paralelo

---

## 📞 Debug Rápido

Se ainda ver erros 500:

1. Verifique `app_debug.log` no servidor Render
2. Procure por "❌ ERRO CRÍTICO: Content vazio"
3. Verifique o tamanho dos documentos (max 30KB de conteúdo textual)
4. Tente enviar documentos menores separadamente
