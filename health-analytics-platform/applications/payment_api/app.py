import random
import time
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "payment-api",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/payments')
def get_payments():
    time.sleep(random.uniform(0.02, 0.06))

    payments = [
        {"id": 1, "amount": 99.99, "status": "completed"},
        {"id": 2, "amount": 149.99, "status": "pending"},
        {"id": 3, "amount": 49.99, "status": "completed"}
    ]

    return jsonify(payments)

@app.route('/api/payments', methods=['POST'])
def create_payment():
    time.sleep(random.uniform(0.1, 0.3))

    return jsonify({
        "id": random.randint(1000, 9999),
        "status": "processing",
        "amount": random.uniform(10, 500)
    }), 201

@app.route('/api/payments/<int:payment_id>')
def get_payment(payment_id):
    time.sleep(random.uniform(0.03, 0.1))

    return jsonify({
        "id": payment_id,
        "amount": random.uniform(10, 500),
        "status": random.choice(["completed", "pending", "failed"])
    })

@app.route('/api/payments/<int:payment_id>/refund', methods=['POST'])
def refund_payment(payment_id):
    time.sleep(random.uniform(0.15, 0.25))

    return jsonify({
        "id": payment_id,
        "status": "refunded"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001)