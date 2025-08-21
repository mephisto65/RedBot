#!/usr/bin/env python3

from flask import Flask, request, jsonify
from secure_command_executor import SecureCommandExecutor
import logging
import os
import time

app = Flask(__name__)
executor = SecureCommandExecutor(timeout=120)

# Configuration de l'authentification (désactivée)
# API_KEY = os.environ.get("API_KEY", "pentest-api-key-2024")

def require_api_key(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Authentification désactivée
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok", 
        "timestamp": time.time(),
        "message": "LLM Pentest API is running"
    })

@app.route('/commands/allowed', methods=['GET'])
@require_api_key
def get_allowed_commands():
    return jsonify(executor.get_allowed_commands())

@app.route('/execute', methods=['POST'])
@require_api_key
def execute_command():
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({"error": "Commande manquante"}), 400
        
        command = data['command']
        working_dir = data.get('working_dir')
        
        result = executor.execute_command(command, working_dir)
        
        return jsonify({
            "success": result.success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.return_code,
            "execution_time": result.execution_time,
            "command": result.command,
            "category": result.category.value if result.category else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("Démarrage de l'API LLM Pentest sur le port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False)