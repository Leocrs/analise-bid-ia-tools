# 🔒 Configuração Segura da API Key

## ⚠️ IMPORTANTE: Segurança da API Key

A API Key da OpenAI **NUNCA** deve estar exposta no frontend. Ela fica protegida no servidor como variável de ambiente.

## 🚀 Configuração no Vercel

### Passo 1: Acessar Configurações
1. Vá para: https://vercel.com/dashboard
2. Selecione o projeto `analise-bid-ia-tools`
3. Clique em **Settings** → **Environment Variables**

### Passo 2: Adicionar Variável
1. **Name**: `OPENAI_API_KEY`
2. **Value**: `[SUA_CHAVE_OPENAI_AQUI]` (copie do arquivo ANOTACOES_IMPORTANTES.txt)
3. **Environment**: Production, Preview, Development (todos)
4. Clique em **Save**

### Passo 3: Redeploy
1. Vá para **Deployments**
2. Clique nos **...** do último deploy
3. Selecione **Redeploy**

## ✅ Verificação
Após o redeploy, a aplicação funcionará automaticamente com a API Key protegida no servidor.

## 🔧 Para Desenvolvimento Local
```bash
# Copie o .env.example para .env
cp .env.example .env

# Edite o .env e adicione sua chave
OPENAI_API_KEY=sua-chave-aqui
```

## 🛡️ Segurança Garantida
- ✅ API Key apenas no servidor
- ✅ Nunca exposta no browser
- ✅ Não aparece no código fonte
- ✅ Protegida nas variáveis de ambiente