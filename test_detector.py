#!/usr/bin/env python
"""
Test script for enhanced ScamDetector with risk scoring
"""

import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "agentic-honeypot"))

from detector.scam_detector import ScamDetector

def print_result(title, message, result):
    """Pretty print detection results"""
    print(f"\n{'='*70}")
    print(f"TEST: {title}")
    print(f"{'='*70}")
    print(f"Message: {message}")
    print(f"\nResults:")
    print(f"  ✓ Is Scam: {result['is_scam']}")
    print(f"  ✓ Risk Score: {result['risk_score']} (threshold: 0.7)")
    print(f"  ✓ Scam Type: {result['scam_type']}")
    print(f"  ✓ Detected Keywords: {len(result['detected_keywords'])}")
    
    if result['detected_keywords']:
        print(f"\n  Top Keywords by Risk:")
        for i, kw in enumerate(result['detected_keywords'][:5], 1):
            print(f"    {i}. '{kw['keyword']}' - Score: {kw['risk_score']} | Contribution: {kw['contribution']}")
    
    print(f"\n  Reason: {result['reason']}")

def main():
    """Run comprehensive tests"""
    detector = ScamDetector()
    
    print("\n" + "="*70)
    print("AGENTIC HONEYPOT - SCAM DETECTOR WITH RISK SCORING")
    print("="*70)
    print("\nFeatures:")
    print("  ✓ Risk-scored keywords (46 total)")
    print("  ✓ Multi-level risk categorization")
    print("  ✓ Keyword frequency analysis")
    print("  ✓ Scam type classification")
    print("  ✓ Detailed detection breakdown")
    
    # Test 1: Phishing
    result1 = detector.detect("Please verify your account immediately by clicking here!")
    print_result(
        "Phishing Attack",
        "Please verify your account immediately by clicking here!",
        result1
    )
    
    # Test 2: Lottery Scam
    result2 = detector.detect("Congratulations! You won the lottery prize! Claim your reward now!")
    print_result(
        "Lottery Scam",
        "Congratulations! You won the lottery prize! Claim your reward now!",
        result2
    )
    
    # Test 3: Financial Scam
    result3 = detector.detect("Your account is suspended! Update your payment information urgently right now!")
    print_result(
        "Financial Scam",
        "Your account is suspended! Update your payment information urgently right now!",
        result3
    )
    
    # Test 4: Account Threat
    result4 = detector.detect("Security alert: Your account has been compromised. Verify immediately!")
    print_result(
        "Account Threat",
        "Security alert: Your account has been compromised. Verify immediately!",
        result4
    )
    
    # Test 5: Normal Message (No Scam)
    result5 = detector.detect("How are you today? Hope to see you soon.")
    print_result(
        "Normal Message (No Scam)",
        "How are you today? Hope to see you soon.",
        result5
    )
    
    # Test 6: Borderline Case
    result6 = detector.detect("Dear customer, please contact us for support.")
    print_result(
        "Borderline Case",
        "Dear customer, please contact us for support.",
        result6
    )
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    test_results = [result1, result2, result3, result4, result5, result6]
    scams_detected = sum(1 for r in test_results if r['is_scam'])
    print(f"Total Tests: {len(test_results)}")
    print(f"Scams Detected: {scams_detected}")
    print(f"Normal Messages: {len(test_results) - scams_detected}")
    print(f"\nAverage Risk Score: {round(sum(r['risk_score'] for r in test_results) / len(test_results), 3)}")
    
    # Keyword Statistics
    all_keywords = []
    for result in test_results:
        all_keywords.extend([kw['keyword'] for kw in result['detected_keywords']])
    print(f"Total Keywords Detected: {len(all_keywords)}")
    print(f"Unique Keywords: {len(set(all_keywords))}")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
