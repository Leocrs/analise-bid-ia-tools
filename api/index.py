import sqlite3
import os
import signal
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime

# 🔧 Função para forçar logs aparecerem em qualquer lugar
def log_debug(msg):
    """Force log to appear in Render/console AND file"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_msg = f"[{timestamp}] {msg}"
    
    # 1. Console stdout
    print(log_msg, flush=True)
    sys.stdout.flush()
    
    # 2. Console stderr
    sys.stderr.write(f"{log_msg}\n")
    sys.stderr.flush()
    
    # 3. File (persists data)
    try:
        log_file = os.path.join(os.path.dirname(__file__), 'app_debug.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{log_msg}\n")
            f.flush()
    except:
        pass

# Função para inicializar o banco e criar tabela se não existir
def init_db():
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'historico_base.db')
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                prompt TEXT,
                resposta TEXT,
                data DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Criar tabela de configurações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT UNIQUE,
                modelo TEXT DEFAULT 'gpt-5',
                max_tokens INTEGER DEFAULT 8000,
                chunk_size INTEGER DEFAULT 8000,
                data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Banco de dados inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")

# Pool de conexões para SQLite
@contextmanager
def get_db_connection():
    conn = None
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'historico_base.db')
        conn = sqlite3.connect(db_path, timeout=10)
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Erro na conexão com banco: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Inicializar banco ao iniciar app
init_db()

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# ✅ CONFIGURAR CORS EXPLICITAMENTE
CORS(app, 
     origins=["https://analise-bid-ia-tools.vercel.app", "http://localhost:3000", "http://localhost:5000"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configurações de timeout
REQUEST_TIMEOUT = 120  # 2 minutos para requisições OpenAI
OPENAI_TIMEOUT = 90    # 1.5 minutos para OpenAI especificamente

# Middleware de monitoramento
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    if duration > 5:  # Log apenas requisições longas
        print(f"⚠️ Requisição lenta: {request.endpoint} - {duration:.2f}s")
    return response

# Middleware para limpeza de memória
import gc

@app.teardown_appcontext  
def cleanup(exception):
    gc.collect()  # Forçar garbage collection

# Tratamento de sinais para graceful shutdown
def signal_handler(signum, frame):
    print(f"\n🛑 Recebido sinal {signum}. Finalizando aplicação...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Rota otimizada para servir arquivos estáticos 
@app.route('/static/<path:filename>')
def static_files(filename):
    try:
        static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analise-bid-ia-tools')
        return send_from_directory(static_path, filename, as_attachment=False, cache_timeout=3600)
    except Exception as e:
        print(f"❌ Erro ao servir arquivo estático {filename}: {e}")
        return jsonify({'error': 'Arquivo não encontrado'}), 404

# Inicializar o cliente OpenAI com configurações otimizadas
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=OPENAI_TIMEOUT,
    max_retries=2
)

# Função para processar requisição com timeout
def process_openai_request(messages, model, max_tokens, retry_attempt=1):
    """Processa requisição OpenAI com controle de timeout"""
    try:
        log_debug(f"\n🤖 === CHAMANDO OPENAI (Tentativa {retry_attempt}) ===")
        log_debug(f"   Model: {model}")
        log_debug(f"   Max Tokens: {max_tokens}")
        log_debug(f"   Temperature: 1 (GPT-5 obrigatório)")
        log_debug(f"   Número de mensagens: {len(messages)}")
        for idx, msg in enumerate(messages):
            msg_content = msg.get('content', '')
            msg_role = msg.get('role', 'unknown')
            content_preview = msg_content[:50] + "..." if len(msg_content) > 50 else msg_content
            log_debug(f"   • Mensagem {idx+1} ({msg_role}): {len(msg_content)} chars - {repr(content_preview)}")
        
        # Validação: mensagens não podem estar vazias
        for msg in messages:
            if not msg.get('content') or not msg.get('content').strip():
                log_debug(f"❌ ERRO: Mensagem de role '{msg.get('role')}' está vazia!")
                raise ValueError(f"Mensagem de role '{msg.get('role')}' está vazia")
        
        # GPT-5 usa max_completion_tokens em vez de max_tokens
        # GPT-5 requer temperature=1 (não suporta outros valores)
        log_debug("   ⏳ Aguardando resposta da OpenAI...")
        
        # Adicionar timeout mais curto para testar
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_completion_tokens=max_tokens,  # Corrigido para GPT-5
            temperature=1,  # GPT-5 só aceita valor padrão (1)
            timeout=OPENAI_TIMEOUT
        )
        log_debug("   ✅ Resposta recebida da OpenAI")
        
        # 🔍 LOG DETALHADO DA RESPOSTA
        log_debug(f"\n🔎 === ANALISANDO RESPOSTA DO OPENAI ===")
        log_debug(f"   Tipo do response: {type(response).__name__}")
        log_debug(f"   Has .choices: {hasattr(response, 'choices')}")
        
        if not hasattr(response, 'choices'):
            log_debug("   ❌ Response não tem atributo 'choices'!")
            return response, None
            
        if not response.choices:
            log_debug("   ❌ response.choices está vazio!")
            return response, None
        
        choice = response.choices[0]
        log_debug(f"   Número de choices: {len(response.choices)}")
        log_debug(f"   Choice[0] type: {type(choice).__name__}")
        log_debug(f"   Has .message: {hasattr(choice, 'message')}")
        
        if not hasattr(choice, 'message'):
            log_debug("   ❌ Choice não tem atributo 'message'!")
            return response, None
        
        msg = choice.message
        log_debug(f"   Message type: {type(msg).__name__}")
        log_debug(f"   Has .content: {hasattr(msg, 'content')}")
        
        if not hasattr(msg, 'content'):
            log_debug("   ❌ Message não tem atributo 'content'!")
            return response, None
        
        content = msg.content
        log_debug(f"   Content type: {type(content).__name__}")
        log_debug(f"   Content value: {repr(content) if content else 'NULO/VAZIO'}")
        log_debug(f"   Content length: {len(content) if content else 0}")
        log_debug(f"   Is None: {content is None}")
        log_debug(f"   Is empty string: {content == ''}")
        log_debug(f"   Is whitespace only: {content.isspace() if isinstance(content, str) else 'N/A'}")
        log_debug("🔎 === FIM DA ANÁLISE ===\n")
        
        return response, None
    except Exception as e:
        print(f"\n❌ ERRO ao chamar OpenAI:")
        print(f"   Tipo do erro: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return None, str(e)

# Função assíncrona para salvar histórico
def save_to_history_async(usuario, prompt, resposta):
    """Salva histórico de forma assíncrona para não bloquear resposta"""
    def save_task():
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO historico (usuario, prompt, resposta) VALUES (?, ?, ?)',
                    (usuario, str(prompt), resposta)
                )
                conn.commit()
                print("✅ Histórico salvo com sucesso")
        except Exception as e:
            print(f"❌ Erro ao salvar histórico: {e}")
    
    # Executar em thread separada
    thread = threading.Thread(target=save_task)
    thread.daemon = True
    thread.start()

@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()
    
    try:
        data = request.json
        messages = data.get('messages', [])
        model = data.get('model', 'gpt-5')
        # OTIMIZAÇÃO: Reduzir max_tokens para evitar out of memory
        # GPT-5 funciona bem com 4000 tokens mantendo qualidade de análise
        max_tokens = min(data.get('max_tokens', 4000), 32000)
        
        log_debug("🚀 === NOVA REQUISIÇÃO DE ANÁLISE ===")
        log_debug(f"📧 Modelo: {model}")
        log_debug(f"🔢 Max Tokens (otimizado): {max_tokens}")
        log_debug(f"📝 Total de mensagens: {len(messages)}")
        
        # 🔍 DEBUG: Mostrar conteúdo das mensagens para diagnosticar problemas
        for idx, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content_size = len(msg.get('content', ''))
            log_debug(f"   Mensagem {idx + 1} ({role}): {content_size} chars")
            if role == 'user' and content_size < 200:
                log_debug(f"      [⚠️ Mensagem do usuário muito pequena!]")
                log_debug(f"      Conteúdo: {repr(msg.get('content', '')[:100])}")
        
        log_debug("=" * 50)

        # Validação básica
        if not messages:
            log_debug('❌ Nenhuma mensagem fornecida')
            return jsonify({'error': 'Nenhuma mensagem fornecida'}), 400
        
        # ⚠️ VALIDAÇÃO CRÍTICA: Se a mensagem do usuário estiver vazia, é um problema!
        user_message = next((m for m in messages if m.get('role') == 'user'), None)
        if not user_message or not user_message.get('content', '').strip():
            log_debug("❌ ERRO: Mensagem do usuário está VAZIA!")
            log_debug(f"   Messages recebidas: {messages}")
            return jsonify({'error': 'Mensagem do usuário está vazia - não é possível processar'}), 400
        
        # OTIMIZAÇÃO: Reduzir limite de tamanho total para economizar memória
        # Consolidação muito grande de documentos causa out of memory
        tamanho_messages = len(str(messages))
        truncado = False
        
        if tamanho_messages > 30000:  # Reduzido de 50000 para 30000
            log_debug(f"⚠️ AVISO: Prompt muito longo ({tamanho_messages} chars), truncando documentos...")
            truncado = True
            # Truncar mensagem do usuário se muito grande
            for msg in messages:
                if msg.get('role') == 'user' and len(msg.get('content', '')) > 20000:
                    tamanho_antes = len(msg.get('content', ''))
                    msg['content'] = msg['content'][:20000] + "\n\n[⚠️ DOCUMENTO TRUNCADO - LIMITE DE MEMÓRIA DO SERVIDOR]"
                    log_debug(f"   📄 Documento reduzido de {tamanho_antes} para 20000 caracteres")
            log_debug("✅ Documentos truncados com sucesso")

        # 🔍 LOG: Mostrar conteúdo completo do prompt que será enviado
        log_debug("🔍 === PROMPT ENVIADO PARA OPENAI ===")
        for idx, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            log_debug(f"\n📌 MENSAGEM {idx + 1} ({role}):")
            if role == 'system':
                log_debug(f"Primeiros 200 chars: {content[:200]}")
            else:
                log_debug(f"Primeiros 300 chars: {content[:300]}")
                log_debug(f"Total: {len(content)} caracteres")
        log_debug("=" * 50)
        
        # Processar requisição OpenAI
        response, error = process_openai_request(messages, model, max_tokens)
        
        if error:
            log_debug(f"❌ ERRO na API OpenAI: {error}")
            log_debug(f"   Mensagens que causaram erro: {len(messages)} mensagens")
            return jsonify({'error': f'Erro na API OpenAI: {error}'}), 500
        
        if not response or not response.choices:
            log_debug("❌ ERRO: Resposta vazia da OpenAI")
            return jsonify({'error': 'Resposta vazia da OpenAI'}), 500

        # ✅ VALIDAÇÃO CRÍTICA: Verificar se content está vazio
        content = response.choices[0].message.content if response.choices[0].message else None
        
        # ✅ VALIDAÇÃO RIGOROSA: Content não pode ser None, vazio ou só espaços
        if not content or not content.strip():
            log_debug("\n" + "="*60)
            log_debug("❌ ERRO CRÍTICO: Content vazio ou só espaços!")
            log_debug(f"   Content recebido: {repr(content)}")
            log_debug(f"   Is None: {content is None}")
            log_debug(f"   Type: {type(content)}")
            log_debug(f"   Len: {len(content) if content else 0}")
            log_debug("="*60)
            
            # 🔄 RETRY: Tentar novamente
            retry_count = 0
            max_retries = 2
            content = None
            
            while retry_count < max_retries and (not content or not content.strip()):
                retry_count += 1
                log_debug(f"\n🔄 🔄 🔄 ACIONANDO RETRY {retry_count} de {max_retries} 🔄 🔄 🔄")
                
                # Aguardar um pouco antes de retry
                time.sleep(2)
                
                response2, error2 = process_openai_request(messages, model, max_tokens, retry_attempt=retry_count+1)
                if error2:
                    log_debug(f"❌ RETRY {retry_count} falhou com erro: {error2}")
                    continue
                
                log_debug(f"   ✅ Retry {retry_count}: Resposta recebida")
                content = response2.choices[0].message.content if response2 and response2.choices else None
                log_debug(f"   Content retry {retry_count}: {repr(content[:100] if content else 'VAZIO')}")
            
            if not content or not content.strip():
                log_debug("❌ ERRO CRÍTICO: Todas as tentativas falharam!")
                log_debug(f"   Total de tentativas: {retry_count + 1}")
                log_debug("   ⚠️ GPT-5 continua retornando vazio")
                log_debug("   Possíveis causas: Token limit atingido, API indisponível, ou conteúdo muito longo")
                
                # Retornar mensagem mais informativa
                return jsonify({
                    'error': 'OpenAI não conseguiu processar sua requisição. Possíveis causas: documentos muito grandes, limite de tokens ou indisponibilidade da API. Tente novamente ou com documentos menores.'
                }), 500
            
            log_debug(f"✅ ✅ ✅ RETRY BEM-SUCEDIDO! ✅ ✅ ✅")
            log_debug(f"   Tamanho do conteúdo: {len(content)} chars")
            log_debug(f"   Primeiros 100 chars: {content[:100]}")
        
        processing_time = time.time() - start_time
        log_debug(f"✅ Resposta da OpenAI recebida com sucesso!")
        log_debug(f"📄 Tamanho da resposta: {len(content)} caracteres")
        
        # VALIDAÇÃO: Avisar se a análise pode estar incompleta
        if truncado and len(content) < 500:
            log_debug("⚠️ AVISO: Resposta muito curta - análise pode estar incompleta!")
            log_debug(f"   Tamanho da resposta: {len(content)} caracteres")
            content += "\n\n⚠️ **AVISO:** A análise pode estar incompleta devido ao tamanho dos documentos. Para análise completa, envie documentos menores separadamente."
        
        log_debug(f"⏱️ Tempo de processamento: {processing_time:.2f}s")
        log_debug("=" * 50)

        # Salvar histórico de forma assíncrona
        save_to_history_async(
            data.get('usuario', 'anonimo'),
            messages,
            content
        )

        return jsonify({
            'choices': [{
                'message': {
                    'content': content
                }
            }],
            'processing_time': round(processing_time, 2)
        })
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Erro interno do servidor: {str(e)}"
        print(f"❌ ERRO GERAL: {error_msg}")
        print(f"⏱️ Tempo até erro: {processing_time:.2f}s")
        print("=" * 50)
        return jsonify({'error': error_msg}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de saúde com informações detalhadas"""
    try:
        # Testar conexão com banco
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM historico')
            total_records = cursor.fetchone()[0]
        
        return jsonify({
            "status": "ok",
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "database_working": True,
            "total_records": total_records,
            "timeout_config": {
                "request_timeout": REQUEST_TIMEOUT,
                "openai_timeout": OPENAI_TIMEOUT
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "database_working": False,
            "error": str(e)
        }), 500

@app.route('/api/historico', methods=['GET'])
def get_historico():
    """Endpoint otimizado para buscar histórico"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Limitar resultados para evitar sobrecarga
        limit = min(limit, 100)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, usuario, prompt, resposta, data FROM historico ORDER BY data DESC LIMIT ? OFFSET ?',
                (limit, offset)
            )
            rows = cursor.fetchall()
            
            # Contar total de registros
            cursor.execute('SELECT COUNT(*) FROM historico')
            total = cursor.fetchone()[0]
        
        historico = [
            {
                'id': row[0],
                'usuario': row[1],
                'prompt': row[2][:500] + '...' if len(row[2]) > 500 else row[2],  # Truncar prompt longo
                'resposta': row[3][:1000] + '...' if len(row[3]) > 1000 else row[3],  # Truncar resposta longa
                'data': row[4]
            }
            for row in rows
        ]
        
        return jsonify({
            'historico': historico,
            'total': total,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        print(f"❌ Erro ao buscar histórico: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Endpoint para recuperar configurações do usuário"""
    try:
        # Tentar obter API Key do header
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key', 'default')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT modelo, max_tokens, chunk_size FROM configuracoes WHERE api_key = ?',
                (api_key,)
            )
            row = cursor.fetchone()
        
        if row:
            return jsonify({
                'modelo': row[0],
                'max_tokens': row[1],
                'chunk_size': row[2],
                'cached': False
            })
        else:
            # Retornar valores padrão se não encontrado
            return jsonify({
                'modelo': 'gpt-5',
                'max_tokens': 8000,
                'chunk_size': 8000,
                'cached': True
            })
    except Exception as e:
        print(f"❌ Erro ao buscar configurações: {e}")
        return jsonify({
            'modelo': 'gpt-5',
            'max_tokens': 8000,
            'chunk_size': 8000,
            'error': str(e),
            'cached': True
        }), 200  # Retornar 200 mesmo com erro para fallback

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Endpoint para salvar configurações do usuário"""
    try:
        data = request.json
        api_key = data.get('api_key', 'default')
        modelo = data.get('modelo', 'gpt-5')
        max_tokens = data.get('max_tokens', 8000)
        chunk_size = data.get('chunk_size', 8000)
        
        # Validações básicas
        if max_tokens < 100 or max_tokens > 128000:
            return jsonify({'error': 'max_tokens deve estar entre 100 e 128000'}), 400
        
        if chunk_size < 100 or chunk_size > 128000:
            return jsonify({'error': 'chunk_size deve estar entre 100 e 128000'}), 400
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Tentar atualizar, senão inserir (UPSERT)
            cursor.execute('''
                INSERT INTO configuracoes (api_key, modelo, max_tokens, chunk_size)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(api_key) 
                DO UPDATE SET 
                    modelo = excluded.modelo,
                    max_tokens = excluded.max_tokens,
                    chunk_size = excluded.chunk_size,
                    data_atualizacao = CURRENT_TIMESTAMP
            ''', (api_key, modelo, max_tokens, chunk_size))
            conn.commit()
        
        print(f"✅ Configurações salvas para API Key: {api_key[:10]}...")
        return jsonify({
            'success': True,
            'message': 'Configurações salvas com sucesso',
            'modelo': modelo,
            'max_tokens': max_tokens,
            'chunk_size': chunk_size
        })
    except Exception as e:
        print(f"❌ Erro ao salvar configurações: {e}")
        return jsonify({'error': str(e)}), 500

# Rota otimizada para servir arquivos da pasta App-IA
@app.route('/App-IA/<path:filename>')
def serve_app_ia_files(filename):
    try:
        app_ia_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
        return send_from_directory(app_ia_path, filename, as_attachment=False, cache_timeout=3600)
    except Exception as e:
        print(f"❌ Erro ao servir arquivo App-IA {filename}: {e}")
        return jsonify({'error': 'Arquivo não encontrado'}), 404

# 🔍 ENDPOINT DE DIAGNÓSTICO - Testa GPT-5 diretamente
@app.route('/api/test-gpt5', methods=['POST'])
def test_gpt5():
    """
    Endpoint APENAS PARA DIAGNÓSTICO - Testa GPT-5 com um prompt simples.
    Útil para verificar se GPT-5 está retornando conteúdo vazio.
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        test_message = data.get('message', 'Teste simples: responda "OK"')
        
        print("\n" + "="*60)
        print("🔍 DIAGNÓSTICO: Testando GPT-5 diretamente")
        print(f"   Mensagem de teste: {test_message[:50]}...")
        print("="*60)
        
        # Teste com mensagem simples
        messages = [
            {
                "role": "system",
                "content": "Você é um assistente de diagnóstico. Responda breve e claramente."
            },
            {
                "role": "user", 
                "content": test_message
            }
        ]
        
        # Chamar process_openai_request com 4000 tokens (mesmo que /api/chat)
        response, error = process_openai_request(messages, 'gpt-5', 4000)
        
        if error:
            print(f"❌ ERRO: {error}")
            return jsonify({
                'status': 'erro',
                'erro': error,
                'tempo': round(time.time() - start_time, 2)
            }), 500
        
        if not response or not response.choices:
            print("❌ Resposta vazia (sem choices)")
            return jsonify({
                'status': 'erro',
                'erro': 'Resposta vazia (sem choices)',
                'tempo': round(time.time() - start_time, 2)
            }), 500
        
        content = response.choices[0].message.content
        
        print(f"\n✅ DIAGNÓSTICO COMPLETADO")
        print(f"   Content: {repr(content[:100] if content else 'VAZIO')}")
        print(f"   Tamanho: {len(content) if content else 0} chars")
        print(f"   Tempo: {time.time() - start_time:.2f}s")
        print("="*60 + "\n")
        
        return jsonify({
            'status': 'sucesso' if content else 'aviso',
            'content': content,
            'tamanho': len(content) if content else 0,
            'content_is_empty': not content or not content.strip(),
            'tempo': round(time.time() - start_time, 2)
        })
        
    except Exception as e:
        print(f"❌ ERRO em /api/test-gpt5: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'status': 'erro',
            'erro': str(e),
            'tempo': round(time.time() - start_time, 2)
        }), 500

# Rota otimizada para a página principal
@app.route('/')
def index():
    try:
        app_ia_path = os.path.dirname(os.path.dirname(__file__))
        return send_file(os.path.join(app_ia_path, 'index.html'))
    except Exception as e:
        print(f"❌ Erro ao servir página principal: {e}")
        return jsonify({'error': 'Página não encontrado'}), 404

# 🔍 ROTA DE DEBUG: Servir página de debug dos logs
@app.route('/debug-logs')
@app.route('/debug_logs.html')
def debug_logs_page():
    """Serve a página de debug dos logs"""
    try:
        app_ia_path = os.path.dirname(os.path.dirname(__file__))
        return send_file(os.path.join(app_ia_path, 'debug_logs.html'))
    except Exception as e:
        log_debug(f"❌ Erro ao servir debug_logs.html: {e}")
        return jsonify({'error': 'Página de debug não encontrada'}), 404

# 🔍 ROTA DE DEBUG: Acessar logs
@app.route('/api/debug-logs', methods=['GET'])
def get_debug_logs():
    """Retorna os últimos 100 logs do arquivo app_debug.log"""
    try:
        log_file = os.path.join(os.path.dirname(__file__), 'app_debug.log')
        if not os.path.exists(log_file):
            return jsonify({'logs': 'Nenhum log disponível ainda'}), 200
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Retorna os últimos 200 logs
        recent_logs = ''.join(lines[-200:])
        
        return jsonify({
            'logs': recent_logs,
            'total_lines': len(lines),
            'last_updated': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🔍 ROTA DE DEBUG: Limpar logs
@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    """Limpa o arquivo de log"""
    try:
        log_file = os.path.join(os.path.dirname(__file__), 'app_debug.log')
        if os.path.exists(log_file):
            open(log_file, 'w').close()
            return jsonify({'status': 'Logs limpos com sucesso'}), 200
        return jsonify({'status': 'Arquivo de log não existe'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 TOOLS ENGENHARIA - DOCUMENT AI ANALYZER BACKEND")
    print("=" * 70)
    print("🌐 Servidor Flask iniciado em: http://localhost:5000")
    print("🤖 OpenAI API: Configurada e pronta")
    print("📊 Endpoints disponíveis:")
    print("   • POST /api/chat - Análise de documentos")
    print("   • GET  /api/health - Status do sistema")
    print("   • GET  /api/historico - Histórico de análises")
    print("   • GET  / - Interface principal")
    print("=" * 70)
    print("💡 Logs da aplicação aparecerão abaixo:")
    print("=" * 70)
    
    # Para desenvolvimento local
    app.run(debug=False, port=5000, threaded=True)

# Para produção (Render/Vercel)
app = app