#!/usr/bin/env python3

from flask import Flask, request, jsonify
from secure_command_executor import SecureCommandExecutor
import logging
import threading
import time
import psutil

############### UTILS ###############

processes={} # Dictionary to hold background processes info

def get_background_output(pid, stream_type='both', last_n_lines=None):

    result = {}

    if stream_type in ['stdout', 'both']:
        stdout_lines = processes[pid]['stdout']
        if last_n_lines:
            stdout_lines = stdout_lines[-last_n_lines:]
        result['stdout'] = stdout_lines
        
    if stream_type in ['stderr', 'both']:
        stderr_lines = processes[pid]['stderr']
        if last_n_lines:
            stderr_lines = stderr_lines[-last_n_lines:]
        result['stderr'] = stderr_lines
        
    return result

def start_output_monitoring(pid, process):
    """Démarre le monitoring des sorties pour un processus"""
    
    # Thread pour stdout
    stdout_thread = threading.Thread(
        target=_read_stream,
        args=(process.stdout, processes[pid]["stdout"], 'stdout'),
        daemon=True
    )
    
    # Thread pour stderr - FIXED: Added target= and args=
    stderr_thread = threading.Thread(
        target=_read_stream,
        args=(process.stderr, processes[pid]["stderr"], 'stderr'),
        daemon=True
    )
    
    stdout_thread.start()
    stderr_thread.start()
    
    return True

def _read_stream(stream, buffer, stream_name):
    """Lit un stream et stocke les lignes dans le buffer"""
    try:
        # IMPORTANT: Make sure the stream is in text mode for readline()
        for line in iter(stream.readline, ''):
            if line:
                timestamp = time.time()
                buffer.append({
                    'timestamp': timestamp,
                    'line': line.rstrip('\n'),
                    'stream': stream_name
                })
            else:
                break
    except Exception as e:
        # Add the error to the buffer so you can see what went wrong
        buffer.append({
            'timestamp': time.time(),
            'line': f"⚠️ Error reading {stream_name} stream: {str(e)}",
            'stream': 'error'
        })
    finally:
        if hasattr(stream, 'close'):
            stream.close()

def _read_stream(stream, buffer,stream_name):
    """Lit un stream et stocke les lignes dans le buffer"""
    try:
        for line in iter(stream.readline, ''):
            if line:
                timestamp = time.time()
                buffer.append({
                    'timestamp': timestamp,
                    'line': line.rstrip('\n'),
                    'stream': stream_name
                })
            else:
                break
    except Exception as e:
        return f"⚠️ Error reading {stream_name} stream: {str(e)}"
    finally:
        stream.close()

###################################################################

app = Flask(__name__)
executor = SecureCommandExecutor(timeout=120)
port = 7289 # TODO CONFIGURE PORT

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok", 
        "timestamp": time.time(),
        "message": "LLM Pentest API is running"
    })

@app.route('/commands/allowed', methods=['GET'])
def get_allowed_commands():
    return jsonify(executor.get_allowed_commands())

@app.route('/background/<int:pid>', methods=['GET'])
def get_background_process(pid):
    """Récupère les informations d'un processus par son PID"""
    try:
        # Vérifier si le processus existe
        if not psutil.pid_exists(pid):
            return jsonify({
                'error': 'Process not found',
                'pid': pid
            }), 404
        
        # Obtenir les informations du processus
        process = psutil.Process(pid)
        output = get_background_output(pid, stream_type='both')
        
        process_info = {
            # 'pid': pid,
            # 'name': process.name(),
            # 'status': process.status(),
            # 'cpu_percent': process.cpu_percent(),
            # 'memory_info': process.memory_info()._asdict(),
            # 'create_time': process.create_time(),
            # 'cmdline': process.cmdline(),
            # 'cwd': process.cwd() if process.cwd() else None,
            # 'children': [child.pid for child in process.children()],
            'stdout': output.get('stdout', []),
            'stderr': output.get('stderr', [])
        }
        
        return jsonify({
            'success': True,
            'process': process_info
        }), 200
        
    except psutil.NoSuchProcess:
        return jsonify({
            'error': 'Process no longer exists',
            'pid': pid
        }), 404
    except psutil.AccessDenied:
        return jsonify({
            'error': 'Access denied to process information',
            'pid': pid
        }), 403
    except Exception as e:
        return jsonify({
            'error': str(e),
            'pid': pid
        }), 500

@app.route('/execute/background', methods=['POST'])
def execute_background_command():
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({"error": "Missing command"}), 400
        
        command = data['command']
        
        result,pid,process = executor.execute_background_command(command)

        processes[pid]={"stdout":[],"stderr":[]}
        start_output_monitoring(pid,process)

        return jsonify({
            "success": result.success,
            "PID": pid,
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/execute', methods=['POST'])
def execute_command():
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({"error": "Missing command"}), 400
        
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
    print(f"Starting LLM Pentest API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)