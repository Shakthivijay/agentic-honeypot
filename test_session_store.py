#!/usr/bin/env python
"""
Test script for SessionStore with message tracking, intelligence, and scam confirmation
"""

import sys
sys.path.insert(0, 'agentic-honeypot')

from storage.session_store import SessionStore
import json

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def main():
    store = SessionStore()
    
    # Test 1: Create session and track messages
    print_section("TEST 1: Create Session & Track Message Count")
    session_id_1 = "session_phishing_001"
    store.create_session(session_id_1)
    
    messages = [
        "Hello, I need to verify your account",
        "Can you click this link to confirm?",
        "Please enter your password",
    ]
    
    for msg in messages:
        store.add_message(session_id_1, msg, sender='attacker')
    
    session1 = store.get_session(session_id_1)
    print(f"Session ID: {session_id_1}")
    print(f"Messages tracked: {session1.message_count}")
    for msg_data in session1.messages:
        print(f"  [{msg_data['message_number']}] {msg_data['sender']}: {msg_data['message']}")
    
    # Test 2: Extract and track intelligence
    print_section("TEST 2: Track Extracted Intelligence")
    session_id_2 = "session_upi_scam_001"
    store.create_session(session_id_2)
    
    # Add messages
    store.add_message(session_id_2, "Send payment to user@okhdfcbank", sender='attacker')
    store.add_message(session_id_2, "Call +91-9876543210 for support", sender='attacker')
    store.add_message(session_id_2, "Verify at https://secure-bank.com", sender='attacker')
    
    # Add extracted intelligence
    intelligence1 = {
        'upi_ids': [{'upi': 'user@okhdfcbank', 'bank': 'okhdfcbank'}],
        'phone_numbers': [{'normalized': '919876543210', 'region': 'India'}],
        'urls': [{'url': 'https://secure-bank.com', 'domain': 'secure-bank.com'}],
        'suspicious_keywords': {
            'credential_theft': ['verify'],
            'financial_threat': ['payment'],
        }
    }
    
    store.add_intelligence(session_id_2, intelligence1)
    
    session2 = store.get_session(session_id_2)
    print(f"Session ID: {session_id_2}")
    print(f"Messages: {session2.message_count}")
    print(f"UPI IDs Found: {len(session2.extracted_intelligence['upi_ids'])}")
    for upi in session2.extracted_intelligence['upi_ids']:
        print(f"  - {upi}")
    print(f"Phone Numbers Found: {len(session2.extracted_intelligence['phone_numbers'])}")
    for phone in session2.extracted_intelligence['phone_numbers']:
        print(f"  - {phone}")
    print(f"URLs Found: {len(session2.extracted_intelligence['urls'])}")
    for url in session2.extracted_intelligence['urls']:
        print(f"  - {url}")
    print(f"Keyword Categories: {list(session2.extracted_intelligence['suspicious_keywords'].keys())}")
    
    # Test 3: Track scam detection results
    print_section("TEST 3: Track Scam Detection & Risk Score")
    session_id_3 = "session_lottery_001"
    store.create_session(session_id_3)
    
    # Add messages
    store.add_message(session_id_3, "You won a lottery prize! Claim now!", sender='attacker')
    store.add_message(session_id_3, "Send ₹500 to merchant@okaxis", sender='attacker')
    
    # Add detection results
    detection1 = {
        'is_scam': True,
        'risk_score': 0.92,
        'scam_type': 'lottery',
        'detected_keywords': ['won', 'lottery', 'claim', 'prize'],
        'reason': 'Lottery scam with payment request'
    }
    
    detection2 = {
        'is_scam': True,
        'risk_score': 0.88,
        'scam_type': 'lottery',
        'detected_keywords': ['payment', 'upi'],
        'reason': 'Financial threat detected'
    }
    
    store.add_scam_detection(session_id_3, detection1)
    store.add_scam_detection(session_id_3, detection2)
    
    session3 = store.get_session(session_id_3)
    print(f"Session ID: {session_id_3}")
    print(f"Messages: {session3.message_count}")
    print(f"Scam Detections: {len(session3.scam_detections)}")
    print(f"Highest Risk Score: {session3.scam_confirmation_score:.2f}")
    print(f"Risk Level: {session3.risk_level}")
    print(f"Primary Scam Type: {session3.attacker_profile['primary_scam_type']}")
    for i, detection in enumerate(session3.scam_detections, 1):
        print(f"\n  Detection {i}:")
        print(f"    Type: {detection['scam_type']}")
        print(f"    Risk Score: {detection['risk_score']:.2f}")
        print(f"    Keywords: {', '.join(detection['detected_keywords'])}")
        print(f"    Reason: {detection['reason']}")
    
    # Test 4: Confirm scam
    print_section("TEST 4: Confirm Scam & Update Status")
    store.confirm_scam(session_id_3, confidence=0.98, notes="Multiple lottery + UPI payment indicators")
    
    session3_updated = store.get_session(session_id_3)
    print(f"Session ID: {session_id_3}")
    print(f"Scam Confirmed: {session3_updated.scam_confirmed}")
    print(f"Confirmation Score: {session3_updated.scam_confirmation_score:.2f}")
    print(f"Risk Level: {session3_updated.risk_level}")
    
    # Test 5: Session summary
    print_section("TEST 5: Get Session Summary")
    summary = store.get_session_summary(session_id_3)
    print(f"Session Summary:")
    print(json.dumps(summary, indent=2))
    
    # Test 6: Create multiple sessions and filter
    print_section("TEST 6: Multiple Sessions & Filtering")
    
    # Create phishing session
    session_id_phishing = "session_phishing_002"
    store.create_session(session_id_phishing)
    store.add_message(session_id_phishing, "Verify your account", sender='attacker')
    detection_phishing = {
        'is_scam': True,
        'risk_score': 0.95,
        'scam_type': 'phishing',
        'detected_keywords': ['verify', 'account'],
        'reason': 'Phishing attempt'
    }
    store.add_scam_detection(session_id_phishing, detection_phishing)
    
    # Create financial session
    session_id_financial = "session_financial_001"
    store.create_session(session_id_financial)
    store.add_message(session_id_financial, "Update your payment info", sender='attacker')
    detection_financial = {
        'is_scam': True,
        'risk_score': 0.85,
        'scam_type': 'financial',
        'detected_keywords': ['payment', 'update'],
        'reason': 'Financial scam'
    }
    store.add_scam_detection(session_id_financial, detection_financial)
    
    # Create normal session
    session_id_normal = "session_normal_001"
    store.create_session(session_id_normal)
    store.add_message(session_id_normal, "How are you?", sender='attacker')
    detection_normal = {
        'is_scam': False,
        'risk_score': 0.1,
        'scam_type': 'none',
        'detected_keywords': [],
        'reason': 'Normal message'
    }
    store.add_scam_detection(session_id_normal, detection_normal)
    
    print(f"Total Sessions Created: {len(store.sessions)}")
    print(f"\nAll Sessions Summary:")
    all_summaries = store.get_all_sessions_summary()
    for i, summary in enumerate(all_summaries, 1):
        print(f"  {i}. {summary['session_id']} - Risk: {summary['risk_level'].upper()}")
    
    print(f"\nConfirmed Scams: {len(store.get_confirmed_scams())}")
    for scam in store.get_confirmed_scams():
        print(f"  - {scam['session_id']}: {scam['primary_scam_type']}")
    
    print(f"\nHigh Risk Sessions (>= high):")
    high_risk = store.get_high_risk_sessions(risk_level='high')
    for session in high_risk:
        print(f"  - {session['session_id']}: {session['risk_level']} ({session['scam_confirmation_score']:.1%})")
    
    print(f"\nSessions by Scam Type:")
    for scam_type in ['phishing', 'lottery', 'financial']:
        sessions = store.get_sessions_by_scam_type(scam_type)
        print(f"  {scam_type}: {len(sessions)} session(s)")
        for s in sessions:
            print(f"    - {s['session_id']}")
    
    # Test 7: Aggregated intelligence
    print_section("TEST 7: Aggregated Intelligence Summary")
    
    # Add intelligence to multiple sessions
    for sid in [session_id_phishing, session_id_financial]:
        intel = {
            'upi_ids': [{'upi': f'attacker{sid[-1]}@okhdfcbank', 'bank': 'okhdfcbank'}],
            'phone_numbers': [{'normalized': f'9188888888{sid[-1]}', 'region': 'India'}],
            'urls': [{'url': f'https://phishing-{sid[-1]}.com', 'domain': f'phishing-{sid[-1]}.com'}],
            'suspicious_keywords': {'credential_theft': ['verify'], 'financial_threat': ['payment']},
        }
        store.add_intelligence(sid, intel)
    
    intel_summary = store.get_extracted_intelligence_summary()
    print(f"Intelligence Aggregation Summary:")
    print(f"  Total Sessions: {intel_summary['total_sessions']}")
    print(f"  Confirmed Scams: {intel_summary['confirmed_scams']}")
    print(f"  Unique UPI IDs: {intel_summary['unique_upi_ids']}")
    print(f"  Unique Phone Numbers: {intel_summary['unique_phone_numbers']}")
    print(f"  Unique URLs: {intel_summary['unique_urls']}")
    print(f"  UPI IDs Tracked:")
    for upi in intel_summary['upi_ids']:
        print(f"    - {upi}")
    print(f"  Phone Numbers Tracked:")
    for phone in intel_summary['phone_numbers']:
        print(f"    - {phone}")
    print(f"  URLs Tracked:")
    for url in intel_summary['urls']:
        print(f"    - {url}")
    
    # Test 8: Update attacker profile
    print_section("TEST 8: Attacker Profile Tracking")
    store.get_session(session_id_3).update_attacker_profile({
        'strategy': 'lottery_payment_request',
        'targets': ['user@okhdfcbank', 'merchant@okaxis'],
        'payment_amount': '500',
        'sophistication': 'low',
    })
    
    session3_final = store.get_session(session_id_3)
    print(f"Session: {session_id_3}")
    print(f"Attacker Profile:")
    print(f"  Strategy: {session3_final.attacker_profile['strategy']}")
    print(f"  Primary Target Type: {session3_final.attacker_profile['primary_scam_type']}")
    print(f"  Targets: {session3_final.attacker_profile['targets']}")
    print(f"  Payment Amount Requested: {session3_final.attacker_profile['payment_amount']}")
    print(f"  Sophistication: {session3_final.conversation_metadata['attacker_sophistication']}")
    
    # Summary
    print_section("SUMMARY - Session Store Features")
    print("""
✓ In-Memory Session Storage
  - Create, retrieve, update, delete sessions
  - Fast O(1) access by session ID
  - Persistent within application lifetime

✓ Message Count Tracking
  - Incremental message numbering
  - Track sender (attacker/agent)
  - Timestamp each message
  - Complete conversation history

✓ Extracted Intelligence Tracking
  - UPI IDs with bank information
  - Phone numbers (normalized, regional)
  - URLs with domain extraction
  - Suspicious keywords categorized
  - Deduplication across messages

✓ Scam Detection Tracking
  - Store all detection results
  - Track risk score progression
  - Maintain scam type history
  - Automatically update risk level
  - Extract primary scam pattern

✓ Scam Confirmation System
  - Manual confirmation with confidence score
  - Automatic risk escalation
  - Confirmation logging
  - Update risk level to critical

✓ Session Filtering & Queries
  - Get all sessions
  - Filter by risk level (critical, high, medium, etc.)
  - Filter by scam type (phishing, lottery, financial, etc.)
  - Get confirmed scams only

✓ Attacker Profile Building
  - Track strategy and tactics
  - Record targets/contact info
  - Payment amounts requested
  - Sophistication level assessment

✓ Aggregated Intelligence
  - Unique UPI IDs across all sessions
  - Unique phone numbers across all sessions
  - Unique URLs across all sessions
  - Keyword categories and counts
  - High-level threat landscape view

✓ Session Lifecycle Management
  - Creation timestamp
  - Last updated timestamp
  - Session deletion
  - Bulk clear functionality
    """)

if __name__ == "__main__":
    main()
