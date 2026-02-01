Set-Location "c:\Users\SHAKTHI\Desktop\agentic-honeypot\agentic-honeypot"
Write-Host "Starting Agentic Honeypot Server..." -ForegroundColor Green
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Documentation at: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
