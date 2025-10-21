# 🚀 TOOLS ENGENHARIA - Document AI Analyzer

Sistema avançado de análise de documentos usando IA, otimizado para ambientes de produção com alta performance e estabilidade.

## ✨ Funcionalidades

- 🤖 **Análise Inteligente**: Processamento de documentos usando GPT-4
- 📊 **Interface Moderna**: Dashboard interativo e responsivo
- 💾 **Histórico Persistente**: Armazenamento de análises em SQLite
- ⚡ **Alta Performance**: Otimizado para ambientes de produção
- 🔒 **Seguro**: Tratamento robusto de erros e timeouts
- 📈 **Monitoramento**: Logs detalhados e métricas de performance

## 🛠️ Melhorias Implementadas (21/10/2025)

### Performance e Estabilidade

- ✅ **Configuração otimizada do Gunicorn** com timeouts adequados
- ✅ **Pool de conexões SQLite** para melhor concorrência
- ✅ **Salvamento assíncrono** do histórico
- ✅ **Garbage collection** automático
- ✅ **Tratamento de sinais** para graceful shutdown

### Timeouts e Limites

- ✅ **Timeout OpenAI**: 90 segundos
- ✅ **Timeout requisições**: 180 segundos
- ✅ **Limite de tokens**: 4000 máximo
- ✅ **Limite de prompt**: 50KB máximo
- ✅ **Reinício de workers**: A cada 500 requisições

### Monitoramento

- ✅ **Health check** completo
- ✅ **Métricas de performance**
- ✅ **Logs estruturados**
- ✅ **Detecção de requisições lentas**

## 🚀 Deploy

### Arquivos de Configuração

- `gunicorn.conf.py` - Configuração otimizada do Gunicorn
- `start.sh` - Script de inicialização
- `build.sh` - Script de build atualizado

### Comandos de Deploy

```bash
# Build
./build.sh

# Start
./start.sh
```

## 📊 Endpoints API

### Chat Analysis

```
POST /api/chat
```

### Health Check

```
GET /api/health
```

### Histórico

```
GET /api/historico?limit=50&offset=0
```

---

**TOOLS ENGENHARIA** - Sistema de Análise de Documentos com IA  
✅ **Problema resolvido**: Worker timeout e SIGKILL eliminados  
⚡ **Performance**: Otimizada para produção  
🔧 **Estabilidade**: Máxima confiabilidade
