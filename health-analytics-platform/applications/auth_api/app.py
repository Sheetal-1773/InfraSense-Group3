import random
import time
import hashlib
from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

sessions = {}


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "auth-api",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    time.sleep(random.uniform(0.05, 0.15))

    data = request.get_json() or {}
    username = data.get('username', '')

    session_token = hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()

    sessions[session_token] = {
        "username": username,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
    }

    return jsonify({
        "token": session_token,
        "expires_in": 86400
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        if token in sessions:
            del sessions[token]

    return jsonify({"status": "logged_out"})

@app.route('/api/auth/verify', methods=['POST'])
def verify():
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return jsonify({"valid": False}), 401

    token = auth_header[7:]

    if token in sessions:
        session = sessions[token]
        return jsonify({
            "valid": True,
            "username": session["username"]
        })

    return jsonify({"valid": False}), 401

@app.route('/api/auth/refresh', methods=['POST'])
def refresh():
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "No token provided"}), 401

    token = auth_header[7:]

    if token not in sessions:
        return jsonify({"error": "Invalid token"}), 401

    new_token = hashlib.sha256(f"refresh{time.time()}".encode()).hexdigest()
    sessions[new_token] = {
        "username": sessions[token]["username"],
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
    }

    del sessions[token]

    return jsonify({
        "token": new_token,
        "expires_in": 86400
    })

@app.route('/api/users')
def get_users():
    time.sleep(random.uniform(0.02, 0.08))

    users = [
        {"id": 1, "username": "admin", "role": "admin"},
        {"id": 2, "username": "user1", "role": "user"},
        {"id": 3, "username": "user2", "role": "user"}
    ]

    return jsonify(users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4002)