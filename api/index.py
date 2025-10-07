from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        api_key = data.get('api_key')
        messages = data.get('messages', [])
        model = data.get('model', 'gpt-4')
        max_tokens = data.get('max_tokens', 2000)
        temperature = data.get('temperature', 0.7)
        
        print("🚀 === NOVA REQUISIÇÃO DE ANÁLISE ===")
        print(f"📧 Modelo: {model}")
        print(f"🔢 Max Tokens: {max_tokens}")
        print(f"📝 Total de mensagens: {len(messages)}")
        print("=" * 50)
        
        if not api_key:
            return jsonify({'error': 'API Key é obrigatória'}), 400
        
        # Criar cliente OpenAI com a chave fornecida
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
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
        print(f"❌ ERRO na API OpenAI: {str(e)}")
        print("=" * 50)
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "Vercel Deployment"})

# For Vercel
app = app