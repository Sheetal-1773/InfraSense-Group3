import random
import time
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "customer-api",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/customers')
def get_customers():
    time.sleep(random.uniform(0.01, 0.05))

    customers = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
    ]

    return jsonify(customers)

@app.route('/api/customers/<int:customer_id>')
def get_customer(customer_id):
    time.sleep(random.uniform(0.02, 0.08))

    return jsonify({
        "id": customer_id,
        "name": f"Customer {customer_id}",
        "email": f"customer{customer_id}@example.com"
    })

@app.route('/api/customers', methods=['POST'])
def create_customer():
    time.sleep(random.uniform(0.05, 0.15))

    return jsonify({"id": random.randint(100, 999), "status": "created"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)