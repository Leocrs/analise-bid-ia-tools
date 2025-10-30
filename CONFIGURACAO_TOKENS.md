# 📊 CONFIGURAÇÃO DE TOKENS - MAPA COMPLETO

## 🎯 RESUMO RÁPIDO

```
Frontend (index.html):       4000 tokens ✅
Backend /api/chat:          4000 tokens ✅
Backend /api/test-gpt5:     4000 tokens ✅
Máximo permitido:          32000 tokens
```

---

## 📱 FRONTEND - index.html

### Local 1: Campo de entrada (linha 72)
```html
<input type="number" id="maxTokens" value="4000" placeholder="4000" />
```
**O que é**: Campo visual onde o usuário pode alterar max_tokens
**Valor padrão**: 4000

### Local 2: Ao carregar configurações (linha 498)
```javascript
document.getElementById("maxTokens").value = data.max_tokens || 4000;
```
**O que faz**: Se o backend retornar max_tokens, usa-o. Senão, 4000.

### Local 3: Ao iniciar a página (linha 521)
```javascript
const maxTokens = localStorage.getItem("max_tokens") || 4000;
```
**O que faz**: Recupera do localStorage, senão 4000

### Local 4: Ao enviar para backend (linha 554)
```javascript
max_tokens: parseInt(maxTokens),
```
**O que faz**: Converte para inteiro e envia para /api/chat

---

## 🔧 BACKEND - api/index.py

### Fluxo do /api/chat (Análise Principal)

#### Linha 228: Recebe do frontend
```python
max_tokens = min(data.get('max_tokens', 4000), 32000)
```
**O que faz**:
- Se frontend mandar max_tokens: usa esse valor
- Se não mandar: usa padrão 4000
- Se mandar > 32000: reduz para 32000 (proteção de memória)

**Resultado**: max_tokens fica entre 4000 e 32000

#### Linha 232: Log
```python
print(f"🔢 Max Tokens (otimizado): {max_tokens}")
```
**O que vê**: Mostra qual valor está sendo usado

#### Linha 143: Chama OpenAI
```python
response = client.chat.completions.create(
    model=model,
    messages=messages,
    max_completion_tokens=max_tokens,  # ← AQUI!
    temperature=1,
    timeout=OPENAI_TIMEOUT
)
```
**O que faz**: Passa para GPT-5 o max_tokens definido

---

### Fluxo do /api/test-gpt5 (Diagnóstico)

#### Linha 573: Chamada direto
```python
response, error = process_openai_request(messages, 'gpt-5', 4000)
```
**O que faz**: Testa GPT-5 com 4000 tokens sempre

---

## 🔄 FLUXO COMPLETO (De ponta a ponta)

```
1. FRONTEND inicia
   ↓
2. Carrega localStorage ou usa 4000
   ↓
3. Exibe "4000" no campo de entrada
   ↓
4. Usuário clica "Analisar"
   ↓
5. Frontend envia: { max_tokens: 4000, ... } 
   ↓
6. BACKEND recebe em /api/chat
   ↓
7. Backend processa: max_tokens = min(4000, 32000) = 4000
   ↓
8. Backend chama GPT-5: max_completion_tokens=4000
   ↓
9. GPT-5 responde (com até 4000 tokens)
   ↓
10. Backend retorna resposta
    ↓
11. Frontend exibe resposta
```

---

## 🚨 PROBLEMAS ANTERIORES (RESOLVIDOS)

| Problema | Antes | Agora | Fixo? |
|----------|-------|-------|-------|
| Frontend enviando max_tokens | ❌ Não enviava | ✅ Envia 4000 | ✅ SIM |
| Backend usando max_tokens | ❌ Ignorava | ✅ Usa com min() | ✅ SIM |
| /api/test-gpt5 usando tokens | ❌ 1000 | ✅ 4000 | ✅ SIM |
| GPT-5 API recebendo tokens | ✅ Sim | ✅ Sim | ✅ OK |
| GPT-5 retornando vazio | ❌ Retorna "" | ❓ Em teste | ⏳ TESTE |

---

## 📋 CONFIGURAÇÕES SECUNDÁRIAS (Outras APIs)

### /api/settings (linha 475)
```python
'max_tokens': 8000,  # ← PADRÃO de settings
```
**Use para**: Alterar padrão global de max_tokens

### /api/save_settings (linha 496)
```python
max_tokens = data.get('max_tokens', 8000)
```
**Use para**: Salvar novo padrão via API

---

## ✅ CHECKLIST DE TOKENS

- [x] Frontend envia 4000
- [x] Backend recebe 4000
- [x] Backend passa 4000 para GPT-5
- [x] Backend máximo: 32000
- [x] Diagnóstico também com 4000
- [x] Logs mostram qual valor está sendo usado
- [ ] GPT-5 retorna resposta com 4000 tokens (TESTANDO)

---

## 🎯 PRÓXIMO PASSO

Execute o teste no endpoint `/api/test-gpt5` com **4000 tokens** e veja se:
- ✅ GPT-5 consegue responder com 4000 tokens
- ❌ GPT-5 continua retornando vazio (mesmo com 4000)

Se retornar vazio com 4000 também, o problema NÃO é a quantidade de tokens!
