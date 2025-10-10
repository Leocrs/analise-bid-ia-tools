
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from openai import OpenAI
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
CORS(app)

# Configurar API Key do ambiente (seguro)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️ AVISO: OPENAI_API_KEY não configurada nas variáveis de ambiente")

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    print("[LOG] Início do endpoint /api/chat")
    try:
        data = request.get_json()
        print(f"[LOG] Dados recebidos: {data}")
        messages = data.get('messages', [])
        model = data.get('model', 'gpt-3.5-turbo')
        max_tokens = data.get('max_tokens', 100)
        temperature = data.get('temperature', 0.7)
        
        print("🚀 === NOVA REQUISIÇÃO DE ANÁLISE ===")
        print(f"📧 Modelo: {model}")
        print(f"🔢 Max Tokens: {max_tokens}")
        print(f"🌡️ Temperatura: {temperature}")
        print(f"📝 Total de mensagens: {len(messages)}")
        print("=" * 50)
        
        if not OPENAI_API_KEY:
            return jsonify({'error': 'Serviço temporariamente indisponível. API Key não configurada no servidor.'}), 503
        
        # Criar cliente OpenAI com a chave do servidor (seguro) - sem proxies
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        print("[LOG] Resposta gerada com sucesso")
        print("[LOG] Fim do endpoint /api/chat")
        
        print("✅ Resposta da OpenAI recebida com sucesso!")
        print(f"📄 Tamanho da resposta: {len(response.choices[0].message.content)} caracteres")
        print("=" * 50)
        
        return jsonify({
            'choices': [{
                'message': {
                    'content': response.choices[0].message.content
                }
            }]
        })
        
    except Exception as e:
        import traceback
        print(f"❌ ERRO na API OpenAI: {str(e)}")
        traceback.print_exc()
        print("=" * 50)
        # Sempre retorna JSON, mesmo em erro
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


# Health check para Render
@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": "ok", "service": "Render Deployment", "timestamp": "2025-10-10-19:15"})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "Vercel Deployment"})

# For Vercel
app = app