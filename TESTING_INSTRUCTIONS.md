# Agentic Honeypot API - Testing Guide

## ✅ Server Status
**Server is running at: `http://127.0.0.1:8000`**

### Auto-generated Documentation
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## 🚀 How to Start the Server

### Option 1: Using PowerShell Script (Recommended)
```powershell
powershell -ExecutionPolicy Bypass -File "c:\Users\SHAKTHI\Desktop\agentic-honeypot\START_SERVER.ps1"
```

### Option 2: Manual Command
```bash
cd c:\Users\SHAKTHI\Desktop\agentic-honeypot\agentic-honeypot
python -m uvicorn app:app --reload
```

---

## 🧪 Testing the Endpoints

### Environment Setup
```powershell
$API_KEY = "your-secret-api-key-here"
$BASE_URL = "http://127.0.0.1:8000"
$HEADERS = @{
    "x-api-key" = $API_KEY
    "Content-Type" = "application/json"
}
```

---

## 📋 Available Endpoints

### 1. Health Check
**GET** `/health` - Check if server is running

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET | ConvertFrom-Json
```

**Response:**
```json
{
  "status": "healthy",
  "service": "agentic-honeypot"
}
```

---

### 2. **[PRIMARY] Honeypot Message** ⭐
**POST** `/honeypot/message` - Main conversation endpoint with session tracking

**Parameters:**
- `sessionId` (string) - Unique session identifier
- `message` (string) - The incoming message
- `conversationHistory` (array, optional) - Previous conversation messages
- `metadata` (object, optional) - Additional context

```powershell
$payload = @{
    sessionId = "session-001"
    message = "Click here to verify your account immediately!"
    conversationHistory = @()
    metadata = @{
        source = "email"
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
    }
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri "http://127.0.0.1:8000/honeypot/message" `
    -Method POST `
    -Headers @{"x-api-key" = "your-secret-api-key-here"} `
    -ContentType "application/json" `
    -Body $payload
```

**Response:**
```json
{
  "sessionId": "session-001",
  "reply": "Dummy response to: 'Click here to verify your account immediately!'. Session session-001 is active.",
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
```

---

### 3. Scam Detection
**POST** `/detect` - Detect scams in messages

```powershell
$payload = @{
    message = "You won a lottery prize! Claim now!"
    source = "email"
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri "http://127.0.0.1:8000/detect" `
    -Method POST `
    -Headers @{"x-api-key" = "your-secret-api-key-here"} `
    -ContentType "application/json" `
    -Body $payload
```

**Response (Scam Detected):**
```json
{
  "is_scam": true,
  "confidence": 0.75,
  "scam_type": "lottery",
  "agent_reply": "This is likely a lottery scam. Legitimate lotteries do not require upfront payments.",
  "action_taken": "block_and_report"
}
```

**Response (No Scam):**
```json
{
  "is_scam": false,
  "confidence": 0.0,
  "scam_type": null,
  "agent_reply": null,
  "action_taken": "message_logged"
}
```

---

### 4. Batch Detection
**POST** `/detect-batch` - Process multiple messages at once

```powershell
$payload = @(
    @{ message = "Update your payment information now!" },
    @{ message = "Your account needs verification" },
    @{ message = "This is a normal message" }
) | ConvertTo-Json

Invoke-WebRequest `
    -Uri "http://127.0.0.1:8000/detect-batch" `
    -Method POST `
    -Headers @{"x-api-key" = "your-secret-api-key-here"} `
    -ContentType "application/json" `
    -Body $payload
```

**Response:**
```json
{
  "total": 3,
  "results": [
    {
      "is_scam": true,
      "confidence": 0.67,
      "scam_type": "financial",
      "agent_reply": "This looks like a financial scam...",
      "action_taken": "flag_and_investigate"
    },
    {
      "is_scam": true,
      "confidence": 0.75,
      "scam_type": "phishing",
      "agent_reply": "This appears to be a phishing attempt...",
      "action_taken": "quarantine_and_alert_user"
    },
    {
      "is_scam": false,
      "confidence": 0.0,
      "scam_type": null,
      "agent_reply": null,
      "action_taken": "message_logged"
    }
  ]
}
```

---

### 5. Root Endpoint
**GET** `/` - API information

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -Method GET | ConvertFrom-Json
```

---

## 🔒 Authentication Testing

### Missing API Key (Expected: 401 Unauthorized)
```powershell
$payload = @{
    sessionId = "test"
    message = "test"
    conversationHistory = @()
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri "http://127.0.0.1:8000/honeypot/message" `
    -Method POST `
    -ContentType "application/json" `
    -Body $payload `
    -ErrorAction SilentlyContinue
```

### Invalid API Key (Expected: 403 Forbidden)
```powershell
$badHeaders = @{
    "x-api-key" = "wrong-key-12345"
    "Content-Type" = "application/json"
}

Invoke-WebRequest `
    -Uri "http://127.0.0.1:8000/honeypot/message" `
    -Method POST `
    -Headers $badHeaders `
    -ContentType "application/json" `
    -Body $payload `
    -ErrorAction SilentlyContinue
```

---

## 📊 Scam Detection Test Cases

### Phishing Detection
```
Message: "Please verify your account by clicking here immediately!"
Expected: is_scam = true, scam_type = "phishing"
```

### Lottery Scam Detection
```
Message: "Congratulations! You won $1,000,000! Claim your prize now!"
Expected: is_scam = true, scam_type = "lottery"
```

### Financial Scam Detection
```
Message: "Your payment method has expired. Update it now to continue."
Expected: is_scam = true, scam_type = "financial"
```

### Normal Message (No Scam)
```
Message: "Hello, how are you doing today?"
Expected: is_scam = false
```

---

## 🔄 Multi-turn Conversation Testing

```powershell
$sessionId = "session-conv-001"
$conversationHistory = @()
$messages = @(
    "Can you help me verify my account?",
    "I need to update my payment details",
    "Where do I click?"
)

foreach ($msg in $messages) {
    Write-Host "User: $msg"
    $payload = @{
        sessionId = $sessionId
        message = $msg
        conversationHistory = $conversationHistory
    } | ConvertTo-Json

    $response = Invoke-WebRequest `
        -Uri "http://127.0.0.1:8000/honeypot/message" `
        -Method POST `
        -Headers @{"x-api-key" = "your-secret-api-key-here"} `
        -ContentType "application/json" `
        -Body $payload

    $data = $response.Content | ConvertFrom-Json
    Write-Host "Agent: $($data.reply)"
    $conversationHistory = $data.conversationHistory
    Write-Host ""
}
```

---

## 🐍 Python Testing

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "your-secret-api-key-here"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

# Test 1: Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Test 2: Honeypot message
payload = {
    "sessionId": "session-123",
    "message": "Click here to verify your account!",
    "conversationHistory": []
}
response = requests.post(
    f"{BASE_URL}/honeypot/message",
    headers=HEADERS,
    json=payload
)
print(json.dumps(response.json(), indent=2))

# Test 3: Scam detection
payload = {"message": "You won a prize! Claim now!"}
response = requests.post(
    f"{BASE_URL}/detect",
    headers=HEADERS,
    json=payload
)
print(json.dumps(response.json(), indent=2))
```

---

## 📝 Key Configuration Values

**API Key:** `your-secret-api-key-here`  
**Server Host:** `127.0.0.1`  
**Server Port:** `8000`  
**Debug Mode:** `False`  
**Scam Confidence Threshold:** `0.7`

---

## ✨ Features Implemented

✅ FastAPI application initialized  
✅ POST `/honeypot/message` endpoint with sessionId, message, conversationHistory  
✅ Scam detection routing  
✅ Agent activation on scam detection  
✅ Conversation history tracking  
✅ API key validation (x-api-key header)  
✅ Dummy response generation  
✅ Batch processing  
✅ Auto-generated API documentation  
✅ Error handling with proper HTTP status codes  

---

## 🎯 Next Steps

1. ✅ Server is running and accessible
2. Start testing with the endpoints above
3. Visit http://127.0.0.1:8000/docs for interactive API testing
4. Customize dummy responses with real agent logic
5. Implement persistent conversation storage
6. Add database integration for session tracking
