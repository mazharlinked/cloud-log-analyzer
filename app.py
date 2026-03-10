# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# ------------------------
# SETTINGS
# ------------------------
USE_REAL_AI = True  # Set True to use OpenAI API when billing is active

if USE_REAL_AI:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------
# Helper: estimate cost
# ------------------------
def estimate_cost(input_tokens, output_tokens, model="gpt-4.1-mini"):
    pricing = {
        "gpt-4.1-mini": {"input": 0.0015, "output": 0.002}  # per 1K tokens
    }
    if model not in pricing:
        return 0.0
    cost = (input_tokens / 1000) * pricing[model]["input"] + \
           (output_tokens / 1000) * pricing[model]["output"]
    return round(cost, 6)

# ------------------------
# Routes
# ------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    logs = request.json.get("logs")
    
    # Rough token estimate: 1 token ≈ 4 chars
    input_tokens = max(1, len(logs) // 4)
    output_tokens = 100  # expected average output
    
    estimated_cost = estimate_cost(input_tokens, output_tokens)
    
    if USE_REAL_AI and openai_available:
        # Real OpenAI API call
        prompt = f"""
You are a cloud reliability engineer.

Analyze these logs and explain:
1. Likely issue
2. Possible root cause
3. Suggested fixes

Logs:
{logs}
"""
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        result_text = response.output_text
    else:
        # Mock response for development/demo
        result_text = f"""
Simulated AI Analysis:
Logs received: {logs}
Detected issue: Simulated service interruption
Suggested fix: Check service health and retry
"""
    
    return jsonify({
        "analysis": result_text,
        "estimated_cost_usd": estimated_cost
    })

# Serve index.html at root
@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

# ------------------------
# Run server
# ------------------------
if __name__ == "__main__":
    app.run(port=5000)