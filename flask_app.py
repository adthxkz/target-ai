from flask import Flask, jsonify
from datetime import datetime
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
if os.path.exists(".env"):
    load_dotenv()

app = Flask(__name__)

# Тестовые данные
MOCK_CAMPAIGNS = [
    {
        "id": "123456789",
        "name": "Test Campaign 1",
        "status": "ACTIVE",
        "objective": "CONVERSIONS",
        "daily_budget": 1000,
        "lifetime_budget": 10000,
        "start_time": "2025-07-01T00:00:00+0000",
        "end_time": "2025-07-31T23:59:59+0000"
    },
    {
        "id": "987654321",
        "name": "Test Campaign 2",
        "status": "PAUSED",
        "objective": "TRAFFIC",
        "daily_budget": 500,
        "lifetime_budget": 5000,
        "start_time": "2025-07-15T00:00:00+0000",
        "end_time": "2025-08-15T23:59:59+0000"
    }
]

@app.route('/')
def root():
    return jsonify({"message": "Target AI API v1.0.0", "status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": str(datetime.now())})

@app.route('/test')
def test():
    return jsonify({"message": "Test endpoint works!", "timestamp": str(datetime.now())})

@app.route('/api/campaigns')
def get_campaigns():
    return jsonify({"campaigns": MOCK_CAMPAIGNS})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
