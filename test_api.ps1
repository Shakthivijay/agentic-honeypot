#!/usr/bin/env powershell
<#
.SYNOPSIS
Testing script for Agentic Honeypot API endpoints
#>

# Configuration
$BASE_URL = "http://127.0.0.1:8000"
$API_KEY = "your-secret-api-key-here"
$HEADERS = @{
    "x-api-key"      = $API_KEY
    "Content-Type"   = "application/json"
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Agentic Honeypot API Testing Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "TEST 1: Health Check Endpoint" -ForegroundColor Yellow
Write-Host "GET $BASE_URL/health" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/health" -Method GET -ErrorAction Stop
    Write-Host "✓ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $(($response.Content | ConvertFrom-Json) | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Root Endpoint
Write-Host "TEST 2: Root Endpoint" -ForegroundColor Yellow
Write-Host "GET $BASE_URL/" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/" -Method GET -ErrorAction Stop
    Write-Host "✓ Status: $($response.StatusCode)" -ForegroundColor Green
    $rootData = $response.Content | ConvertFrom-Json
    Write-Host "Response: $($rootData | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Missing API Key (Should fail)
Write-Host "TEST 3: Missing API Key (Expected to fail)" -ForegroundColor Yellow
Write-Host "POST $BASE_URL/honeypot/message (without API key)" -ForegroundColor Gray
try {
    $payload = @{
        sessionId = "test-session-001"
        message = "Test message"
        conversationHistory = @()
    }
    $response = Invoke-WebRequest -Uri "$BASE_URL/honeypot/message" `
        -Method POST `
        -ContentType "application/json" `
        -Body ($payload | ConvertTo-Json) `
        -ErrorAction Stop
} catch {
    $statusCode = $_.Exception.Response.StatusCode.Value__
    if ($statusCode -eq 401) {
        Write-Host "✓ Correctly rejected (401 Unauthorized)" -ForegroundColor Green
        Write-Host "Error: $(($_.Exception.Response.Content | ConvertFrom-Json).error)" -ForegroundColor Green
    } else {
        Write-Host "✗ Unexpected status: $statusCode" -ForegroundColor Red
    }
}
Write-Host ""

# Test 4: Invalid API Key (Should fail)
Write-Host "TEST 4: Invalid API Key (Expected to fail)" -ForegroundColor Yellow
Write-Host "POST $BASE_URL/honeypot/message (wrong API key)" -ForegroundColor Gray
try {
    $payload = @{
        sessionId = "test-session-001"
        message = "Test message"
        conversationHistory = @()
    }
    $badHeaders = @{
        "x-api-key"    = "wrong-key-12345"
        "Content-Type" = "application/json"
    }
    $response = Invoke-WebRequest -Uri "$BASE_URL/honeypot/message" `
        -Method POST `
        -Headers $badHeaders `
        -ContentType "application/json" `
        -Body ($payload | ConvertTo-Json) `
        -ErrorAction Stop
} catch {
    $statusCode = $_.Exception.Response.StatusCode.Value__
    if ($statusCode -eq 403) {
        Write-Host "✓ Correctly rejected (403 Forbidden)" -ForegroundColor Green
        Write-Host "Error: $(($_.Exception.Response.Content | ConvertFrom-Json).error)" -ForegroundColor Green
    } else {
        Write-Host "✗ Unexpected status: $statusCode" -ForegroundColor Red
    }
}
Write-Host ""

# Test 5: Honeypot Message Endpoint (SUCCESS)
Write-Host "TEST 5: Honeypot Message Endpoint (Valid Request)" -ForegroundColor Yellow
Write-Host "POST $BASE_URL/honeypot/message" -ForegroundColor Gray
try {
    $payload = @{
        sessionId = "session-001"
        message = "Click here to verify your account immediately!"
        conversationHistory = @()
        metadata = @{
            source = "email"
        }
    }
    Write-Host "Request: $(($payload | ConvertTo-Json))" -ForegroundColor Gray
    $response = Invoke-WebRequest -Uri "$BASE_URL/honeypot/message" `
        -Method POST `
        -Headers $HEADERS `
        -ContentType "application/json" `
        -Body ($payload | ConvertTo-Json) `
        -ErrorAction Stop
    Write-Host "✓ Status: $($response.StatusCode)" -ForegroundColor Green
    $respData = $response.Content | ConvertFrom-Json
    Write-Host "Response:" -ForegroundColor Green
    Write-Host ($respData | ConvertTo-Json -Depth 5) -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: Scam Detection Endpoint
Write-Host "TEST 6: Scam Detection Endpoint" -ForegroundColor Yellow
Write-Host "POST $BASE_URL/detect" -ForegroundColor Gray
try {
    $payload = @{
        message = "Congratulations! You won a prize! Claim it now!"
        source = "spam_email"
    }
    Write-Host "Request: $(($payload | ConvertTo-Json))" -ForegroundColor Gray
    $response = Invoke-WebRequest -Uri "$BASE_URL/detect" `
        -Method POST `
        -Headers $HEADERS `
        -ContentType "application/json" `
        -Body ($payload | ConvertTo-Json) `
        -ErrorAction Stop
    Write-Host "✓ Status: $($response.StatusCode)" -ForegroundColor Green
    $respData = $response.Content | ConvertFrom-Json
    Write-Host "Response:" -ForegroundColor Green
    Write-Host ($respData | ConvertTo-Json) -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 7: Multi-turn Conversation
Write-Host "TEST 7: Multi-turn Conversation" -ForegroundColor Yellow
$sessionId = "session-conv-001"
$conversationHistory = @()
$messages = @(
    "Can you help me verify my account?",
    "I need to update my payment details",
    "Where do I click?"
)

foreach ($msg in $messages) {
    Write-Host "User: $msg" -ForegroundColor Cyan
    try {
        $payload = @{
            sessionId = $sessionId
            message = $msg
            conversationHistory = $conversationHistory
        }
        $response = Invoke-WebRequest -Uri "$BASE_URL/honeypot/message" `
            -Method POST `
            -Headers $HEADERS `
            -ContentType "application/json" `
            -Body ($payload | ConvertTo-Json) `
            -ErrorAction Stop
        $respData = $response.Content | ConvertFrom-Json
        Write-Host "Agent: $($respData.reply)" -ForegroundColor Green
        $conversationHistory = $respData.conversationHistory
    } catch {
        Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# Test 8: Batch Detection
Write-Host "TEST 8: Batch Detection Endpoint" -ForegroundColor Yellow
Write-Host "POST $BASE_URL/detect-batch" -ForegroundColor Gray
try {
    $payload = @(
        @{ message = "Update your payment information now!" },
        @{ message = "Your account needs verification" },
        @{ message = "This is a normal message" }
    )
    Write-Host "Request: $(($payload | ConvertTo-Json))" -ForegroundColor Gray
    $response = Invoke-WebRequest -Uri "$BASE_URL/detect-batch" `
        -Method POST `
        -Headers $HEADERS `
        -ContentType "application/json" `
        -Body ($payload | ConvertTo-Json) `
        -ErrorAction Stop
    Write-Host "✓ Status: $($response.StatusCode)" -ForegroundColor Green
    $respData = $response.Content | ConvertFrom-Json
    Write-Host "Response:" -ForegroundColor Green
    Write-Host "Total: $($respData.total)" -ForegroundColor Green
    foreach ($result in $respData.results) {
        Write-Host "  - Is Scam: $($result.is_scam), Confidence: $($result.confidence), Type: $($result.scam_type)" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
