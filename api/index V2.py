import sqlite3
import os
import signal
import sys
import threading
import time
from contextlib import contextmanager

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
CORS(app)

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
def process_openai_request(messages, model, max_tokens):
    """Processa requisição OpenAI com controle de timeout"""
    try:
        print(f"� DEBUG: Preparando requisição para {model}...")
        print(f"   Max Tokens: {max_tokens}")
        print(f"   Messages count: {len(messages)}")
        
        # ⚠️ GPT-5 usa Responses API, não Chat Completions!
        if model.startswith('gpt-5'):
            print("� Usando Responses API para GPT-5...")
            
            # Combinar mensagens para input único (Responses API requer input, não messages)
            user_message = ""
            for msg in messages:
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            response = client.responses.create(
                model=model,
                input=user_message,
                max_output_tokens=max_tokens,
                reasoning={"effort": "low"},  # Baixo esforço para velocidade
                text={"verbosity": "high"}  # Alta verbosidade para análise completa
            )
            print(f"✅ Resposta GPT-5 recebida | Output tokens: {max_tokens}")
            
            # Converter resposta para formato compatível com Chat Completions
            class CompatResponse:
                class Choice:
                    class Message:
                        def __init__(self, content):
                            self.content = content
                    def __init__(self, content):
                        self.message = self.Message(content)
                        self.finish_reason = "stop"
                
                def __init__(self, content):
                    self.choices = [self.Choice(content)]
            
            return CompatResponse(response.output_text), None
        
        else:
            # Chat Completions API para outros modelos (GPT-4, etc)
            print(f"🔄 Usando Chat Completions API para {model}...")
            temperature = 0.7
            
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                    temperature=temperature,
                    timeout=OPENAI_TIMEOUT
                )
                print(f"✅ Usando max_completion_tokens: {max_tokens} | temperature: {temperature}")
                return response, None
            except TypeError:
                # Fallback para versão antiga do SDK
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=OPENAI_TIMEOUT
                )
                print(f"✅ Usando max_tokens (compatibilidade): {max_tokens}")
                return response, None
                
    except Exception as e:
        print(f"❌ ERRO CRÍTICO em process_openai_request: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
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
        model = data.get('model', 'gpt-4')
        max_tokens = min(data.get('max_tokens', 2000), 4000)  # Limitar tokens
        
        print("🚀 === NOVA REQUISIÇÃO DE ANÁLISE ===")
        print(f"📧 Modelo: {model}")
        print(f"🔢 Max Tokens: {max_tokens}")
        print(f"📝 Total de mensagens: {len(messages)}")
        print("=" * 50)

        # Validação básica
        if not messages:
            return jsonify({'error': 'Nenhuma mensagem fornecida'}), 400
        
        if len(str(messages)) > 50000:  # Limitar tamanho do prompt
            return jsonify({'error': 'Prompt muito longo. Reduza o tamanho do texto.'}), 400

        # Processar requisição OpenAI
        response, error = process_openai_request(messages, model, max_tokens)
        
        if error:
            print(f"❌ ERRO na API OpenAI: {error}")
            return jsonify({'error': f'Erro na API OpenAI: {error}'}), 500
        
        if not response:
            print("❌ Response é None!")
            return jsonify({'error': 'Resposta nula da OpenAI'}), 500

        if not response.choices:
            print("❌ Response.choices vazio!")
            return jsonify({'error': 'Resposta vazia da OpenAI (choices vazio)'}), 500

        content = response.choices[0].message.content
        
        if not content:
            print("⚠️ WARNING: Content é None ou vazio!")
            print(f"   Finish reason: {response.choices[0].finish_reason}")
            content = "(Resposta vazia recebida da OpenAI)"
        
        processing_time = time.time() - start_time
        
        print("✅ Resposta da OpenAI recebida com sucesso!")
        print(f"📄 Tamanho da resposta: {len(content) if content else 0} caracteres")
        print(f"⏱️ Tempo de processamento: {processing_time:.2f}s")
        print("=" * 50)

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

# Rota otimizada para a página principal
@app.route('/')
def index():
    try:
        app_ia_path = os.path.dirname(os.path.dirname(__file__))
        return send_file(os.path.join(app_ia_path, 'index.html'))
    except Exception as e:
        print(f"❌ Erro ao servir página principal: {e}")
        return jsonify({'error': 'Página não encontrada'}), 404

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