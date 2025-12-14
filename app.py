
from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Simple storage (will reset on restart - use database in production)
clients = {}
client_counter = 1

# API Key from environment variable
API_KEY = os.environ.get('API_KEY', 'change_this_secret_key_123')


def verify_api_key():
    """Verify the API key from request headers"""
    key = request.headers.get('x-api-key')
    if key != API_KEY:
        return False
    return True


@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        "status": "running",
        "message": "n8n Email Backend API",
        "endpoints": ["/register_client", "/trigger_sequence", "/clients"]
    })


@app.route('/register_client', methods=['POST'])
def register_client():
    """Register a new client"""
    if not verify_api_key():
        return jsonify({"error": "Invalid API key"}), 401
    
    try:
        data = request.json
        global client_counter
        
        client_id = client_counter
        clients[client_id] = {
            "name": data.get("name"),
            "email": data.get("email"),
            "company": data.get("company"),
            "registered_at": datetime.now().isoformat()
        }
        client_counter += 1
        
        return jsonify({
            "client_id": client_id,
            "status": "registered",
            "message": f"Client {data.get('name')} registered successfully"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/trigger_sequence', methods=['POST'])
def trigger_sequence():
    """Trigger an email sequence for a client"""
    if not verify_api_key():
        return jsonify({"error": "Invalid API key"}), 401
    
    try:
        data = request.json
        client_id = data.get("client_id")
        sequence_id = data.get("sequence_id")
        
        if client_id not in clients:
            return jsonify({"error": "Client not found"}), 404
        
        client = clients[client_id]
        
        # Log the sequence trigger
        print(f"Sequence {sequence_id} triggered for client {client_id}: {client['name']}")
        
        return jsonify({
            "status": "sequence_started",
            "client_id": client_id,
            "client_name": client['name'],
            "sequence_id": sequence_id,
            "message": f"Email sequence {sequence_id} started for {client['name']}"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/clients', methods=['GET'])
def get_clients():
    """Get all registered clients"""
    if not verify_api_key():
        return jsonify({"error": "Invalid API key"}), 401
    
    return jsonify({
        "clients": clients,
        "total": len(clients)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

