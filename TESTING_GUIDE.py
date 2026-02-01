"""
Testing Guide for Agentic Honeypot API
"""

# ============================================================================
# 1. START THE SERVER
# ============================================================================
# Run this command in terminal:
# uvicorn app:app --reload

# Server will start at: http://localhost:8000
# Auto-reload is enabled, so changes to code will automatically restart server


# ============================================================================
# 2. API DOCUMENTATION (Auto-generated)
# ============================================================================
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc


# ============================================================================
# 3. TEST ENDPOINTS WITH cURL
# ============================================================================

# Set API Key variable for easy testing:
# $API_KEY = "your-secret-api-key-here"

# ------- 3.1 Health Check Endpoint -------
# PowerShell:
# Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET

# cURL:
# curl -X GET http://localhost:8000/health


# ------- 3.2 Root Endpoint -------
# Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET


# ------- 3.3 Honeypot Message Endpoint (PRIMARY) -------
# This is the main endpoint with sessionId, message, and conversationHistory

# PowerShell:
$body = @{
    sessionId = "session-001"
    message = "Click here to verify your account immediately!"
    conversationHistory = @()
    metadata = @{
        source = "email"
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
    }
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri "http://localhost:8000/honeypot/message" `
    -Method POST `
    -Headers @{"x-api-key" = "your-secret-api-key-here"} `
    -ContentType "application/json" `
    -Body $body


# cURL:
# curl -X POST http://localhost:8000/honeypot/message \
#   -H "x-api-key: your-secret-api-key-here" \
#   -H "Content-Type: application/json" \
#   -d '{"sessionId":"session-001","message":"Click here to verify your account!","conversationHistory":[]}'


# ------- 3.4 Scam Detection Endpoint -------
# This endpoint detects scams without session tracking

# PowerShell:
$detectBody = @{
    message = "Congratulations! You won a prize! Claim it now!"
    source = "text_message"
    timestamp = (Get-Date).ToUniversalTime().ToString("o")
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri "http://localhost:8000/detect" `
    -Method POST `
    -Headers @{"x-api-key" = "your-secret-api-key-here"} `
    -ContentType "application/json" `
    -Body $detectBody


# ------- 3.5 Batch Detection Endpoint -------
# Test multiple messages at once

# PowerShell:
$batchBody = @(
    @{ message = "Update your payment information now!" },
    @{ message = "Your account needs verification" },
    @{ message = "This is a normal message" }
) | ConvertTo-Json

Invoke-WebRequest `
    -Uri "http://localhost:8000/detect-batch" `
    -Method POST `
    -Headers @{"x-api-key" = "your-secret-api-key-here"} `
    -ContentType "application/json" `
    -Body $batchBody


# ============================================================================
# 4. TEST WITH PYTHON (requests library)
# ============================================================================

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

# Test 1: Health Check
print("=== Test 1: Health Check ===")
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Test 2: Honeypot Message (Main endpoint)
print("\n=== Test 2: Honeypot Message ===")
payload = {
    "sessionId": "session-123",
    "message": "Click here to verify your account immediately!",
    "conversationHistory": [],
    "metadata": {"source": "email"}
}
response = requests.post(
    f"{BASE_URL}/honeypot/message",
    headers=HEADERS,
    json=payload
)
print(json.dumps(response.json(), indent=2))

# Test 3: Scam Detection
print("\n=== Test 3: Scam Detection ===")
payload = {
    "message": "You won a lottery prize! Claim now!",
    "source": "spam_email"
}
response = requests.post(
    f"{BASE_URL}/detect",
    headers=HEADERS,
    json=payload
)
print(json.dumps(response.json(), indent=2))

# Test 4: Multi-turn Conversation
print("\n=== Test 4: Multi-turn Conversation ===")
session_id = "session-conv-001"
messages = [
    "Can you help me verify my account?",
    "I need to update my payment details",
    "Where do I click?"
]

conversation_history = []
for msg in messages:
    payload = {
        "sessionId": session_id,
        "message": msg,
        "conversationHistory": conversation_history
    }
    response = requests.post(
        f"{BASE_URL}/honeypot/message",
        headers=HEADERS,
        json=payload
    )
    result = response.json()
    conversation_history = result.get("conversationHistory", [])
    print(f"User: {msg}")
    print(f"Agent: {result.get('reply')}\n")


# ============================================================================
# 5. ERROR TESTING
# ============================================================================

# Test missing API key:
print("=== Test: Missing API Key ===")
response = requests.post(f"{BASE_URL}/honeypot/message", json=payload)
print(response.status_code)  # Should be 401

# Test invalid API key:
print("=== Test: Invalid API Key ===")
bad_headers = {"x-api-key": "wrong-key"}
response = requests.post(
    f"{BASE_URL}/honeypot/message",
    headers=bad_headers,
    json=payload
)
print(response.status_code)  # Should be 403


# ============================================================================
# 6. EXPECTED RESPONSES
# ============================================================================

# Successful /honeypot/message response:
{
    "sessionId": "session-001",
    "reply": "Dummy response to: 'Click here to verify your account!'. Session session-001 is active.",
    "messageId": "session-001_2",
    "timestamp": "2026-02-01T10:30:00.123456",
    "conversationHistory": [
        {
            "role": "user",
            "message": "Click here to verify your account!",
            "timestamp": "2026-02-01T10:30:00.123456"
        },
        {
            "role": "agent",
            "message": "Dummy response to...",
            "timestamp": "2026-02-01T10:30:00.123456"
        }
    ]
}

# Successful /detect response with scam:
{
    "is_scam": true,
    "confidence": 0.75,
    "scam_type": "phishing",
    "agent_reply": "This appears to be a phishing attempt. Please do not provide any personal information.",
    "action_taken": "quarantine_and_alert_user"
}

# ============================================================================
# 7. COMMON TEST SCENARIOS
# ============================================================================

# Phishing Detection:
message = "Please verify your account by clicking here immediately!"

# Lottery Scam:
message = "Congratulations! You won $1,000,000! Claim your prize now!"

# Financial Scam:
message = "Your payment method has expired. Update it now to continue using your account."

# Normal Message (no scam):
message = "Hello, how are you doing today?"
