import sqlite3
import os

# Função para inicializar o banco e criar tabela se não existir
def init_db():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'historico_base.db'))
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
    conn.commit()
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

# Rota para servir arquivos estáticos (css, imagens, js)
@app.route('/static/<path:filename>')
def static_files(filename):
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analise-bid-ia-tools')
    return send_from_directory(static_path, filename)

# Inicializar o cliente OpenAI com a API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    model = data.get('model', 'gpt-4')
    max_tokens = data.get('max_tokens', 2000)
    
    print("🚀 === NOVA REQUISIÇÃO DE ANÁLISE ===")
    print(f"📧 Modelo: {model}")
    print(f"🔢 Max Tokens: {max_tokens}")
    print(f"📝 Total de mensagens: {len(messages)}")
    print("=" * 50)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        print("✅ Resposta da OpenAI recebida com sucesso!")
        print(f"📄 Tamanho da resposta: {len(response.choices[0].message.content)} caracteres")
        print("=" * 50)

        # Salvar histórico no SQLite
        try:
            conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'historico_base.db'))
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO historico (usuario, prompt, resposta) VALUES (?, ?, ?)',
                (
                    data.get('usuario', 'anonimo'),
                    str(messages),
                    response.choices[0].message.content
                )
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERRO] Falha ao salvar histórico no SQLite: {e}")

        return jsonify({
            'choices': [{
                'message': {
                    'content': response.choices[0].message.content
                }
            }]
        })
    except Exception as e:
        print(f"❌ ERRO na API OpenAI: {str(e)}")
        print("=" * 50)
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "openai_configured": bool(os.getenv("OPENAI_API_KEY"))})

@app.route('/api/historico', methods=['GET'])
def get_historico():
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'historico_base.db'))
        cursor = conn.cursor()
        cursor.execute('SELECT id, usuario, prompt, resposta, data FROM historico ORDER BY data DESC')
        rows = cursor.fetchall()
        conn.close()
        historico = [
            {
                'id': row[0],
                'usuario': row[1],
                'prompt': row[2],
                'resposta': row[3],
                'data': row[4]
            }
            for row in rows
        ]
        return jsonify({'historico': historico})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para servir arquivos da pasta App-IA
@app.route('/App-IA/<path:filename>')
def serve_app_ia_files(filename):
    # Pasta pai do backend (App-IA)
    app_ia_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
    return send_from_directory(app_ia_path, filename)

# Rota para a página principal
@app.route('/')
def index():
    app_ia_path = os.path.dirname(os.path.dirname(__file__))
    return send_file(os.path.join(app_ia_path, 'document_ai_app.html'))

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 TOOLS ENGENHARIA - DOCUMENT AI ANALYZER BACKEND")
    print("=" * 70)
    print("🌐 Servidor Flask iniciado em: http://localhost:5000")
    print("🤖 OpenAI API: Configurada e pronta")
    print("📊 Endpoints disponíveis:")
    print("   • POST /api/chat - Análise de documentos")
    print("   • GET  /api/health - Status do sistema")
    print("   • GET  / - Interface principal")
    print("=" * 70)
    print("💡 Logs da aplicação aparecerão abaixo:")
    print("=" * 70)
    
    app.run(debug=True, port=5000)

# For Vercel
app = app