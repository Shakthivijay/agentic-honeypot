"""
FastAPI application for agentic-honeypot - Matches GUVI Problem Statement
REST API for scam detection, agentic engagement, and intelligence extraction
"""

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from detector.scam_detector import ScamDetector
    from agent.agent_brain import AgentBrain
    from extractor.intelligence import IntelligenceExtractor
    from storage.session_store import SessionStore
    from callback.guvi_callback import GuviCallback
    from config import API_KEY, DEBUG, GUVI_ENDPOINT, GUVI_API_KEY, GUVI_TIMEOUT
except ImportError as e:
    print(f"Import Error: {e}")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honeypot",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0"
)

# Initialize components
scam_detector = ScamDetector()
agent_brain = AgentBrain()
intelligence_extractor = IntelligenceExtractor()
session_store = SessionStore()
guvi_callback = GuviCallback(endpoint=GUVI_ENDPOINT, api_key=GUVI_API_KEY, timeout=GUVI_TIMEOUT)


# Request/Response Models - Matching GUVI Problem Statement

class MessageObject(BaseModel):
    """Message object in request"""
    sender: str  # "scammer" or "user"
    text: str    # Message content
    timestamp: str  # ISO-8601 format


class MetadataObject(BaseModel):
    """Metadata object in request"""
    channel: Optional[str] = None  # SMS, WhatsApp, Email, Chat
    language: Optional[str] = None  # Language used
    locale: Optional[str] = None    # Country/region code


class HoneypotRequest(BaseModel):
    """Honeypot API request - Exact format from problem statement"""
    sessionId: str
    message: MessageObject
    conversationHistory: Optional[List[Dict]] = []
    metadata: Optional[MetadataObject] = None


class HoneypotResponse(BaseModel):
    """Honeypot API response - Exact format from problem statement"""
    status: str  # "success" or "error"
    reply: str   # Agent's response


class ExtractedIntelligence(BaseModel):
    """Intelligence extraction format for GUVI callback"""
    upiIds: Optional[List[str]] = []
    phoneNumbers: Optional[List[str]] = []
    phishingLinks: Optional[List[str]] = []
    bankAccounts: Optional[List[str]] = []
    suspiciousKeywords: Optional[List[str]] = []


class GuviCallbackPayload(BaseModel):
    """GUVI evaluation endpoint callback format"""
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str


# Middleware for API key validation
def validate_api_key(x_api_key: str = Header(None)):
    """Validate x-api-key from request headers"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-api-key header"
        )
    
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return x_api_key


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "agentic-honeypot",
        "version": "1.0.0"
    }


# Main API Endpoint - Matches Problem Statement Exactly
@app.post("/api/honeypot/message", response_model=HoneypotResponse, tags=["Honeypot"])
async def honeypot_message_api(
    payload: HoneypotRequest,
    x_api_key: str = Header(None)
):
    """
    Main honeypot message processing endpoint - Matches GUVI Problem Statement
    
    Accepts incoming message events, detects scam intent, activates AI Agent,
    engages scammers in multi-turn conversations, and extracts intelligence.
    
    Request Format:
    {
        "sessionId": "session-id",
        "message": {
            "sender": "scammer",
            "text": "Your account will be blocked...",
            "timestamp": "2026-01-21T10:15:30Z"
        },
        "conversationHistory": [...],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    Response Format:
    {
        "status": "success",
        "reply": "Agent response..."
    }
    """
    
    # Validate API key
    try:
        validate_api_key(x_api_key)
    except HTTPException as e:
        raise e
    
    try:
        session_id = payload.sessionId
        message_text = payload.message.text
        conversation_history = payload.conversationHistory or []
        metadata = payload.metadata
        
        # Get or create session
        session = session_store.get_session(session_id)
        if not session:
            session = session_store.create_session(session_id)
        
        # Extract intelligence from incoming message
        extracted_intel = intelligence_extractor.extract(message_text)
        session_store.add_intelligence(session_id, extracted_intel)
        
        # Add incoming message to session
        session_store.add_message(session_id, message_text, sender=payload.message.sender)
        
        # Detect scam intent
        detection_result = scam_detector.detect(message_text)
        session_store.add_scam_detection(session_id, detection_result)
        
        # Generate agent response
        agent_response = agent_brain.process({
            "message": message_text,
            "scam_type": detection_result.get("scam_type"),
            "risk_score": detection_result.get("risk_score", 0.0),
            "detected_keywords": detection_result.get("detected_keywords", []),
            "conversation_history": conversation_history,
            "metadata": metadata and metadata.dict() or {}
        })
        
        # Add agent response to session
        session_store.add_message(session_id, agent_response.get("reply", ""), sender="agent")
        
        # Prepare response
        response = HoneypotResponse(
            status="success",
            reply=agent_response.get("reply", "")
        )
        
        # If scam is confirmed with high confidence, prepare for GUVI callback
        session_data = session_store.get_session(session_id)
        if session_data and session_data.scam_confirmation_score >= 0.80:
            # Trigger intelligence extraction and GUVI callback
            import threading
            callback_thread = threading.Thread(
                target=send_guvi_callback,
                args=(session_id, session_data)
            )
            callback_thread.daemon = True
            callback_thread.start()
        
        return response
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in honeypot_message_api: {str(e)}")
        if DEBUG:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing honeypot message"
        )


# Helper function to send GUVI callback
def send_guvi_callback(session_id: str, session_data):
    """Send final intelligence to GUVI evaluation endpoint"""
    try:
        # Get session summary
        session_summary = session_store.get_session_summary(session_id)
        
        # Extract intelligence in GUVI format
        intel = session_data.extracted_intelligence
        
        # Build extracted intelligence object
        extracted_intelligence = {
            "upiIds": [
                upi.get('upi') if isinstance(upi, dict) else str(upi)
                for upi in intel.get('upi_ids', [])
            ],
            "phoneNumbers": [
                phone.get('normalized') if isinstance(phone, dict) else str(phone)
                for phone in intel.get('phone_numbers', [])
            ],
            "phishingLinks": [
                url.get('url') if isinstance(url, dict) else str(url)
                for url in intel.get('urls', [])
            ],
            "bankAccounts": [],  # Would extract from conversation if available
            "suspiciousKeywords": list(
                {kw.get('keyword') if isinstance(kw, dict) else str(kw)
                 for category_kws in intel.get('suspicious_keywords', {}).values()
                 for kw in (category_kws if isinstance(category_kws, list) else [])}
            )
        }
        
        # Build GUVI callback payload
        guvi_payload = {
            "sessionId": session_id,
            "scamDetected": session_data.scam_confirmed,
            "totalMessagesExchanged": session_data.message_count,
            "extractedIntelligence": extracted_intelligence,
            "agentNotes": f"Scam Type: {session_data.attacker_profile.get('primary_scam_type')}, "
                         f"Risk Level: {session_data.risk_level}, "
                         f"Confidence: {session_data.scam_confirmation_score:.2f}, "
                         f"Strategy: {session_data.attacker_profile.get('strategy', 'unknown')}"
        }
        
        # Send to GUVI endpoint
        print(f"[GUVI Callback] Sending intelligence for session {session_id} to GUVI endpoint...")
        success, response = guvi_callback.send_intelligence(guvi_payload)
        
        if success:
            print(f"[GUVI Callback] Successfully sent intelligence for {session_id}")
        else:
            print(f"[GUVI Callback] Failed to send intelligence: {response}")
    
    except Exception as e:
        print(f"[GUVI Callback] Error sending callback: {str(e)}")


# Alternative endpoint for explicit GUVI callback submission
@app.post("/api/honeypot/submit-intelligence", tags=["GUVI"])
async def submit_guvi_intelligence(
    session_id: str,
    x_api_key: str = Header(None)
):
    """
    Manually submit final intelligence to GUVI endpoint for a completed session.
    
    Can be called after engagement is complete to ensure intelligence is sent.
    """
    
    try:
        validate_api_key(x_api_key)
    except HTTPException as e:
        raise e
    
    try:
        session_data = session_store.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Send GUVI callback
        send_guvi_callback(session_id, session_data)
        
        return {
            "status": "success",
            "message": f"Intelligence submitted to GUVI for session {session_id}",
            "sessionId": session_id
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        if DEBUG:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting intelligence"
        )


# Get session summary endpoint
@app.get("/api/session/{session_id}", tags=["Session"])
async def get_session_summary(
    session_id: str,
    x_api_key: str = Header(None)
):
    """Get session summary and intelligence"""
    
    try:
        validate_api_key(x_api_key)
    except HTTPException as e:
        raise e
    
    try:
        session_summary = session_store.get_session_summary(session_id)
        if not session_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return session_summary
    
    except HTTPException as e:
        raise e
    except Exception as e:
        if DEBUG:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving session"
        )


# Get all sessions endpoint
@app.get("/api/sessions", tags=["Session"])
async def get_all_sessions(
    x_api_key: str = Header(None)
):
    """Get all sessions summary"""
    
    try:
        validate_api_key(x_api_key)
    except HTTPException as e:
        raise e
    
    try:
        sessions = session_store.get_all_sessions_summary()
        return {
            "total_sessions": len(sessions),
            "sessions": sessions
        }
    
    except Exception as e:
        if DEBUG:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving sessions"
        )


# Root endpoint
@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Agentic Honeypot for Scam Detection & Intelligence Extraction",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "honeypot_message": "/api/honeypot/message (POST)",
            "submit_intelligence": "/api/honeypot/submit-intelligence (POST)",
            "session_summary": "/api/session/{session_id} (GET)",
            "all_sessions": "/api/sessions (GET)"
        },
        "auth": "Requires x-api-key header",
        "problem_statement": "https://guvi.in/honeypot-challenge"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=DEBUG)
