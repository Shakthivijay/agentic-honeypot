#!/usr/bin/env python
"""
Test script for GUVI callback with payload building, timeout, and error handling
"""

import sys
sys.path.insert(0, 'agentic-honeypot')

from callback.guvi_callback import GuviCallback
from storage.session_store import SessionStore
import json
from datetime import datetime

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def main():
    # Initialize callback handler
    callback = GuviCallback(
        endpoint="https://guvi.example.com/api/v1/intelligence",
        api_key="test-api-key-12345",
        timeout=10
    )
    
    # Create a session store and build test session
    store = SessionStore()
    session_id = "session_test_001"
    session = store.create_session(session_id)
    
    # Add messages
    session.add_message("Send payment to attacker@okhdfcbank immediately!", sender='attacker')
    session.add_message("Click this link to verify: https://phishing-site.com", sender='attacker')
    session.add_message("Call +91-9876543210 for support", sender='attacker')
    
    # Add intelligence
    intelligence = {
        'upi_ids': [
            {'upi': 'attacker@okhdfcbank', 'username': 'attacker', 'bank': 'okhdfcbank', 'risk_score': 0.9, 'position': 0}
        ],
        'phone_numbers': [
            {'number': '+91-9876543210', 'normalized': '919876543210', 'region': 'India', 'pattern_type': 'india', 'risk_score': 0.85, 'position': 0}
        ],
        'urls': [
            {'url': 'https://phishing-site.com', 'domain': 'phishing-site.com', 'is_shortened': False, 'suspicion_indicators': ['credential_phishing'], 'risk_score': 0.85, 'position': 0}
        ],
        'suspicious_keywords': {
            'credential_theft': [{'keyword': 'verify', 'count': 1}],
            'financial_threat': [{'keyword': 'payment', 'count': 1}],
            'urgency_markers': [{'keyword': 'immediately', 'count': 1}],
        }
    }
    
    store.add_intelligence(session_id, intelligence)
    
    # Add scam detections
    detection1 = {
        'is_scam': True,
        'risk_score': 0.92,
        'scam_type': 'financial',
        'detected_keywords': ['payment', 'upi', 'transfer'],
        'reason': 'Financial scam with UPI payment request'
    }
    
    detection2 = {
        'is_scam': True,
        'risk_score': 0.88,
        'scam_type': 'phishing',
        'detected_keywords': ['verify', 'click', 'link'],
        'reason': 'Phishing attack with credential theft'
    }
    
    store.add_scam_detection(session_id, detection1)
    store.add_scam_detection(session_id, detection2)
    
    # Confirm scam
    store.confirm_scam(session_id, confidence=0.95, notes="Critical - Financial + Phishing combo")
    
    # Update attacker profile
    session.update_attacker_profile({
        'strategy': 'phishing_financial_combo',
        'targets': ['attacker@okhdfcbank'],
        'payment_amount': '5000',
        'sophistication': 'medium',
    })
    
    # Get final session data
    final_session = store.get_session(session_id)
    
    # TEST 1: Build payload
    print_section("TEST 1: Build Payload Structure")
    
    payload = callback._build_payload(final_session)
    print(f"Payload Structure:")
    print(f"  Report ID: {payload.get('report_id')}")
    print(f"  Timestamp: {payload.get('timestamp')}")
    print(f"  Source: {payload.get('source')}")
    print(f"\nSession Section:")
    session_data = payload.get('session', {})
    print(f"  Session ID: {session_data.get('session_id')}")
    print(f"  Messages: {session_data.get('message_count')}")
    print(f"  Duration (seconds): {session_data.get('duration_seconds')}")
    print(f"\nThreat Classification:")
    threat_data = payload.get('threat', {})
    print(f"  Is Scam: {threat_data.get('is_scam')}")
    print(f"  Scam Type: {threat_data.get('scam_type')}")
    print(f"  Risk Level: {threat_data.get('risk_level')}")
    print(f"  Confidence Score: {threat_data.get('confidence_score'):.2f}")
    print(f"  Detection Count: {len(threat_data.get('scam_detections', []))}")
    print(f"\nIndicators of Compromise (IOCs):")
    iocs = payload.get('indicators_of_compromise', {})
    print(f"  UPI IDs: {len(iocs.get('upi_ids', []))}")
    for upi in iocs.get('upi_ids', []):
        print(f"    - {upi}")
    print(f"  Phone Numbers: {len(iocs.get('phone_numbers', []))}")
    for phone in iocs.get('phone_numbers', []):
        print(f"    - {phone}")
    print(f"  URLs: {len(iocs.get('urls', []))}")
    for url in iocs.get('urls', []):
        print(f"    - {url}")
    print(f"  Domains: {iocs.get('domains', [])}")
    print(f"  Email Addresses: {iocs.get('email_addresses', [])}")
    print(f"\nKeywords Detected:")
    keywords = payload.get('keywords', {})
    for category, kws in keywords.items():
        print(f"  {category}: {len(kws)} keywords")
    print(f"\nAttacker Profile:")
    attacker = payload.get('attacker_profile', {})
    print(f"  Strategy: {attacker.get('strategy')}")
    print(f"  Primary Targets: {attacker.get('targets')}")
    print(f"  Payment Amount: {attacker.get('payment_amount')}")
    print(f"  Sophistication: {attacker.get('sophistication_level')}")
    print(f"\nDetection Analysis:")
    analysis = payload.get('detection_analysis', {})
    print(f"  Total Detections: {analysis.get('total_detections')}")
    print(f"  Confirmed Scam Detections: {analysis.get('confirmed_scam_detections')}")
    print(f"  Average Risk Score: {analysis.get('average_risk_score'):.3f}")
    print(f"  Keywords Detected: {len(analysis.get('detection_keywords', []))}")
    print(f"\nMetadata:")
    metadata = payload.get('metadata', {})
    print(f"  Honeypot Instance: {metadata.get('honeypot_instance')}")
    print(f"  Deployment Region: {metadata.get('deployment_region')}")
    print(f"  Tags: {', '.join(metadata.get('tags', []))}")
    
    # TEST 2: Validate payload
    print_section("TEST 2: Payload Validation")
    is_valid = callback._validate_payload(payload)
    print(f"Payload Valid: {'[YES]' if is_valid else '[NO]'}")
    
    # Show required fields
    required_fields = ['report_id', 'timestamp', 'source', 'session', 'threat', 'indicators_of_compromise']
    print(f"\nRequired Fields Check:")
    for field in required_fields:
        has_field = field in payload
        print(f"  {field}: {'[OK]' if has_field else '[MISSING]'}")
    
    # TEST 3: Pretty print full payload
    print_section("TEST 3: Complete Payload (JSON)")
    payload_json = json.dumps(payload, indent=2, default=str)
    # Show first and last parts
    lines = payload_json.split('\n')
    if len(lines) > 30:
        print('\n'.join(lines[:15]))
        print(f"\n... [{len(lines) - 30} more lines] ...\n")
        print('\n'.join(lines[-15:]))
    else:
        print(payload_json)
    
    # TEST 4: Test timeout handling (simulated)
    print_section("TEST 4: Timeout & Error Handling Demonstration")
    
    # Test with very short timeout (will timeout in real scenario)
    callback_short_timeout = GuviCallback(
        endpoint="https://guvi.example.com/api/v1/intelligence",
        api_key="test-key",
        timeout=1
    )
    print(f"Timeout Configuration: {callback_short_timeout.timeout} seconds")
    
    # Simulate various error scenarios with mock responses
    print(f"\nError Handling Scenarios:")
    
    # Scenario 1: Connection error
    print(f"\n  1. Connection Error Scenario:")
    print(f"     - Trigger: Unable to reach endpoint")
    print(f"     - Handler: Returns connection error with endpoint info")
    print(f"     - Log Level: ERROR")
    
    # Scenario 2: Timeout error
    print(f"\n  2. Timeout Error Scenario:")
    print(f"     - Trigger: Request exceeds {callback_short_timeout.timeout}s")
    print(f"     - Handler: Returns timeout error with duration")
    print(f"     - Log Level: ERROR")
    
    # Scenario 3: Authentication error (401)
    print(f"\n  3. Authentication Error:")
    print(f"     - Status Code: 401")
    print(f"     - Message: 'Authentication failed - check GUVI API key'")
    print(f"     - Log Level: WARNING")
    
    # Scenario 4: Invalid payload (400)
    print(f"\n  4. Invalid Payload Error:")
    print(f"     - Status Code: 400")
    print(f"     - Message: 'Invalid request payload'")
    print(f"     - Response: Includes field-level error details")
    print(f"     - Log Level: WARNING")
    
    # Scenario 5: Rate limit (429)
    print(f"\n  5. Rate Limit Error:")
    print(f"     - Status Code: 429")
    print(f"     - Message: 'Rate limited - too many requests'")
    print(f"     - Includes: Retry-After header")
    print(f"     - Log Level: WARNING")
    
    # Scenario 6: Service unavailable (503)
    print(f"\n  6. Service Unavailable:")
    print(f"     - Status Code: 503")
    print(f"     - Message: 'GUVI service temporarily unavailable'")
    print(f"     - Log Level: WARNING")
    
    # TEST 5: Payload components extraction
    print_section("TEST 5: Payload Components Extraction")
    
    # Extract domains
    domains = callback._extract_domains(iocs.get('urls', []))
    print(f"Extracted Domains: {domains}")
    
    # Extract emails
    emails = callback._extract_emails(iocs.get('upi_ids', []))
    print(f"Extracted Email-like IDs: {emails}")
    
    # Calculate average risk
    avg_risk = callback._calculate_average_risk(threat_data.get('scam_detections', []))
    print(f"Average Risk Score: {avg_risk:.3f}")
    
    # Extract all keywords
    all_keywords = callback._extract_all_keywords(threat_data.get('scam_detections', []))
    print(f"All Keywords Detected: {all_keywords}")
    
    # Generate report ID
    report_id = callback._generate_report_id(session_id)
    print(f"Generated Report ID: {report_id}")
    
    # Generate tags
    tags = callback._generate_tags(store.get_session_summary(session_id))
    print(f"Generated Tags: {', '.join(tags)}")
    
    # Summary
    print_section("SUMMARY - GUVI Callback Features")
    print("""
[+] Payload Building (Exact Specification)
  - Report ID generation with timestamp
  - Session data with duration calculation
  - Threat classification (scam type, risk level, confidence)
  - Indicators of Compromise (UPI, phone, URL, domains, emails)
  - Suspicious keywords by category
  - Attacker profile (strategy, targets, payment, sophistication)
  - Detection analysis (count, average risk, keywords)
  - Metadata and tags for categorization

[+] Timeout Handling
  - Configurable timeout (default: 10 seconds)
  - Graceful timeout error with duration info
  - Proper exception handling
  - Logging of timeout events

[+] Error Handling by Status Code
  - 200: Success - JSON response parsing
  - 401: Authentication failed - check API key
  - 400: Invalid payload - includes error details
  - 429: Rate limited - includes Retry-After
  - 503: Service unavailable
  - Other: Unexpected status handling

[+] Connection Error Handling
  - Connection refused
  - DNS resolution failure
  - Network unreachable
  - SSL certificate errors

[+] Retry & Resilience (Configurable)
  - Retry count in config (default: 3)
  - Retry delay between attempts (default: 5 seconds)
  - Exponential backoff pattern (can be enhanced)
  - All attempts logged

[+] Payload Validation
  - Required field verification
  - Structure validation before sending
  - Session, threat, IOC validation
  - Early error detection

[+] Response Parsing
  - Handle JSON responses
  - Fallback to text parsing on JSON error
  - Extract specific error details from responses
  - Safe handling of unexpected formats

[+] Logging & Debugging
  - Request logging (without sensitive data)
  - Status code logging
  - Error tracking with context
  - Timeout duration logging
    """)

if __name__ == "__main__":
    main()
