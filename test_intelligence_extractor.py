#!/usr/bin/env python
"""
Test script for IntelligenceExtractor with UPI, phone, URL, and keyword extraction
"""

import sys
sys.path.insert(0, 'agentic-honeypot')

from extractor.intelligence import IntelligenceExtractor

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def main():
    extractor = IntelligenceExtractor()
    
    # Test 1: Phishing message with UPI ID
    print_section("TEST 1: Phishing with UPI ID")
    message1 = "Verify your account urgently! Send payment to user@okhdfcbank immediately. Call +91-9876543210 for support."
    result1 = extractor.extract(message1)
    print(f"Message: {message1}\n")
    print(f"UPI IDs Found: {result1['upi_ids']}")
    print(f"Phone Numbers: {result1['phone_numbers']}")
    print(f"Threat Level: {result1['threat_level']} ({result1['confidence']:.1%})")
    print(f"Summary: {extractor.get_summary()}")
    
    # Test 2: Lottery scam with multiple phone numbers and URLs
    print_section("TEST 2: Lottery Scam with Contact Info and URLs")
    message2 = "Congratulations! You won ₹10,00,000. Click here to claim: https://verify-lottery.com/claim. Contact us at +1-202-555-1234 or +91 98765 43210"
    result2 = extractor.extract(message2)
    print(f"Message: {message2}\n")
    print(f"URLs Found: {result2['urls']}")
    print(f"Phone Numbers: {result2['phone_numbers']}")
    print(f"Suspicious Keywords: {list(result2['suspicious_keywords'].keys())}")
    print(f"Threat Level: {result2['threat_level']} ({result2['confidence']:.1%})")
    print(f"Summary: {extractor.get_summary()}")
    
    # Test 3: Financial scam with credential theft indicators
    print_section("TEST 3: Financial Scam - Credential Theft")
    message3 = "Your bank account has been compromised. Verify your credentials immediately at https://secure-bank-login.com. Authentication PIN required. Call 040-2345-6789"
    result3 = extractor.extract(message3)
    print(f"Message: {message3}\n")
    print(f"UPI IDs: {result3['upi_ids']}")
    print(f"URLs: {result3['urls']}")
    print(f"Phone Numbers: {result3['phone_numbers']}")
    print(f"Suspicious Keywords by Category:")
    for category, keywords in result3['suspicious_keywords'].items():
        print(f"  {category}: {[kw['keyword'] for kw in keywords]}")
    print(f"Threat Level: {result3['threat_level']} ({result3['confidence']:.1%})")
    print(f"Summary: {extractor.get_summary()}")
    
    # Test 4: Normal message (low threat)
    print_section("TEST 4: Normal Message - Low Threat")
    message4 = "Hi there! How are you doing today?"
    result4 = extractor.extract(message4)
    print(f"Message: {message4}\n")
    print(f"UPI IDs: {result4['upi_ids']}")
    print(f"Phone Numbers: {result4['phone_numbers']}")
    print(f"URLs: {result4['urls']}")
    print(f"Suspicious Keywords: {result4['suspicious_keywords']}")
    print(f"Threat Level: {result4['threat_level']} ({result4['confidence']:.1%})")
    print(f"Summary: {extractor.get_summary()}")
    
    # Test 5: Complex scam with multiple indicators
    print_section("TEST 5: Complex Scam - Multiple Indicators")
    message5 = """
    URGENT! Your Flipkart account needs immediate verification. 
    Account details compromised. Verify now at https://bit.ly/flipkart-secure
    Send ₹500 as security deposit to merchant@okaxis
    Contact support: +91-8765-432109 or (011) 2345-6789
    Click the link immediately to avoid account suspension!
    """
    result5 = extractor.extract(message5)
    print(f"Message: {message5.strip()}\n")
    print(f"UPI IDs ({len(result5['upi_ids'])}): {[u['upi'] for u in result5['upi_ids']]}")
    print(f"Phone Numbers ({len(result5['phone_numbers'])}): {[p['number'] for p in result5['phone_numbers']]}")
    print(f"URLs ({len(result5['urls'])}): {[u['url'] for u in result5['urls']]}")
    print(f"\nSuspicious Keywords by Category:")
    for category, keywords in result5['suspicious_keywords'].items():
        print(f"  {category}: {[kw['keyword'] for kw in keywords]}")
    print(f"\nThreat Level: {result5['threat_level']} ({result5['confidence']:.1%})")
    print(f"Summary: {extractor.get_summary()}")
    
    # Test 6: URL analysis with suspicion indicators
    print_section("TEST 6: URL Suspicion Analysis")
    message6 = """
    Verify your identity at https://secure-login.com/verify or 
    check this shortened link https://bit.ly/bankupdate or 
    https://tinyurl.com/authentification
    """
    result6 = extractor.extract(message6)
    print(f"Message: {message6.strip()}\n")
    print("URL Analysis:")
    for url in result6['urls']:
        print(f"  URL: {url['url']}")
        print(f"    Domain: {url['domain']}")
        print(f"    Shortened: {url['is_shortened']}")
        print(f"    Suspicion Indicators: {url['suspicion_indicators']}")
        print(f"    Risk Score: {url['risk_score']:.2f}")
    print(f"\nThreat Level: {result6['threat_level']} ({result6['confidence']:.1%})")
    
    # Summary of all tests
    print_section("SUMMARY - Intelligence Extraction Features")
    print("""
✓ UPI ID Extraction
  - Pattern: username@bankname (e.g., user@okhdfcbank)
  - Returns: username, bank name, risk score
  - Use: Identify payment collection targets

✓ Phone Number Extraction
  - Indian format: +91-9xxx, 0-9xxx, 9xxxxxxxxxx
  - International: +1-202-555-1234, (011) 2345-6789
  - Returns: normalized format, region, pattern type
  - Use: Trace attacker contact information

✓ URL Extraction
  - Captures http:// and https:// URLs
  - Detects: shortened URLs, phishing indicators
  - Risk scoring: 0.75-0.99 based on suspicion
  - Use: Identify malicious domains and phishing sites

✓ Suspicious Keyword Extraction
  - 6 categories: financial_threat, urgency_markers, credential_theft,
    social_engineering, action_triggers, reward_baiting
  - Tracks: keyword count, position, risk contribution
  - Use: Classify attack type and intensity

✓ Threat Level Calculation
  - Confidence score: 0.0-1.0 based on all indicators
  - Levels: critical (≥85%), high (65-85%), medium (45-65%), low (25-45%), minimal (<25%)
  - Multipliers: UPI+Phone combo (+15%), Credentials+URL (+10%), Urgency (+5%)
  - Use: Prioritize incident response and investigation

✓ Intelligence Summary
  - Human-readable overview with threat level
  - Emoji indicators for quick visual scanning
  - Use: Logs, reports, admin dashboards
    """)

if __name__ == "__main__":
    main()
