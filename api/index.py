from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import openai

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

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
        messages = data.get('messages', [])
        model = data.get('model', 'gpt-4')
        max_tokens = data.get('max_tokens', 2000)
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return jsonify({
            'choices': [{
                'message': {
                    'content': response.choices[0].message.content
                }
            }],
            'usage': response.usage._asdict() if hasattr(response.usage, '_asdict') else {}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# For Vercel
app = app