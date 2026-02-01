#!/usr/bin/env python
"""
Test script for enhanced AgentBrain with risk-based responses
"""

import sys
sys.path.insert(0, 'agentic-honeypot')

from agent.agent_brain import AgentBrain
import json

def main():
    agent = AgentBrain()
    
    # Test 1: Critical phishing with high risk score
    print("="*70)
    print("TEST 1: Critical Phishing (Risk Score: 0.95)")
    print("="*70)
    result1 = agent.process({
        "message": "Please verify your account immediately by clicking here!",
        "scam_type": "phishing",
        "risk_score": 0.95,
        "detected_keywords": [
            {"keyword": "verify account", "risk_score": 0.95, "contribution": 0.95},
            {"keyword": "immediately", "risk_score": 0.80, "contribution": 0.80}
        ]
    })
    print(f"Strategy: {result1['strategy']}")
    print(f"Engagement: {result1['engagement_level']}")
    print(f"Risk Level: {result1['risk_level']}")
    print(f"Action (Internal): {result1['action']}")
    print(f"\nAgent Reply (Covert):\n{result1['reply']}")
    print()
    
    # Test 2: High risk lottery scam
    print("="*70)
    print("TEST 2: High Risk Lottery Scam (Risk Score: 0.85)")
    print("="*70)
    result2 = agent.process({
        "message": "You won a lottery prize! Claim your reward now!",
        "scam_type": "lottery",
        "risk_score": 0.85,
        "detected_keywords": [
            {"keyword": "won lottery", "risk_score": 0.92, "contribution": 0.92},
            {"keyword": "claim reward", "risk_score": 0.85, "contribution": 0.85}
        ]
    })
    print(f"Strategy: {result2['strategy']}")
    print(f"Engagement: {result2['engagement_level']}")
    print(f"Risk Level: {result2['risk_level']}")
    print(f"Action (Internal): {result2['action']}")
    print(f"\nAgent Reply (Covert):\n{result2['reply']}")
    print()
    
    # Test 3: Medium risk financial scam
    print("="*70)
    print("TEST 3: Medium Risk Financial Scam (Risk Score: 0.70)")
    print("="*70)
    result3 = agent.process({
        "message": "Update your payment info",
        "scam_type": "financial",
        "risk_score": 0.70,
        "detected_keywords": [
            {"keyword": "update payment", "risk_score": 0.90, "contribution": 0.90}
        ]
    })
    print(f"Strategy: {result3['strategy']}")
    print(f"Engagement: {result3['engagement_level']}")
    print(f"Risk Level: {result3['risk_level']}")
    print(f"Action (Internal): {result3['action']}")
    print(f"\nAgent Reply (Covert):\n{result3['reply']}")
    print()
    
    # Test 4: Low risk normal message
    print("="*70)
    print("TEST 4: Low Risk Normal Message (Risk Score: 0.2)")
    print("="*70)
    result4 = agent.process({
        "message": "How are you today?",
        "scam_type": "social_engineering",
        "risk_score": 0.2,
        "detected_keywords": []
    })
    print(f"Strategy: {result4['strategy']}")
    print(f"Engagement: {result4['engagement_level']}")
    print(f"Risk Level: {result4['risk_level']}")
    print(f"Action (Internal): {result4['action']}")
    print(f"\nAgent Reply:\n{result4['reply']}")
    print()
    
    # Test 5: Follow-up engagement for critical phishing
    print("="*70)
    print("TEST 5: Follow-up Engagement (Critical Phishing)")
    print("="*70)
    follow_up = agent.craft_follow_up(
        "Verify your account",
        "phishing",
        0.95
    )
    print(f"Follow-up Message (Asks for More Intel):\n{follow_up}")
    print()
    
    # Test 6: Covert response for escalation
    print("="*70)
    print("TEST 6: Covert Response for Stalling (High Risk Financial)")
    print("="*70)
    covert = agent.get_covert_response_for_escalation("financial", 0.85)
    print(f"Response (Appears to Comply, Actually Stalls):\n{covert}")
    print()
    
    # Test 7: Account threat detection
    print("="*70)
    print("TEST 7: Critical Account Threat (Risk Score: 0.92)")
    print("="*70)
    result7 = agent.process({
        "message": "Your account has been compromised. Verify immediately!",
        "scam_type": "account_threat",
        "risk_score": 0.92,
        "detected_keywords": [
            {"keyword": "compromised", "risk_score": 0.90, "contribution": 0.90},
            {"keyword": "immediately", "risk_score": 0.80, "contribution": 0.80}
        ]
    })
    print(f"Strategy: {result7['strategy']}")
    print(f"Engagement: {result7['engagement_level']}")
    print(f"Risk Level: {result7['risk_level']}")
    print(f"Action (Internal): {result7['action']}")
    print(f"\nAgent Reply (Human-Like, No Detection Revealed):\n{result7['reply']}")
    print()
    
    # Summary
    print("="*70)
    print("SUMMARY - Enhanced Agent Brain Features")
    print("="*70)
    print("✓ Risk-based response calibration")
    print("  - Critical (>0.85): Deep engagement, strong intelligence gathering")
    print("  - High (0.75-0.85): High engagement, sustained investigation")
    print("  - Medium (0.65-0.75): Moderate engagement, observation mode")
    print("  - Low (<0.65): Low engagement, passive monitoring")
    print()
    print("✓ Human-like tone with empathy and genuine interest")
    print("  - Greetings: Friendly, conversational")
    print("  - Responses: Show concern, ask clarifying questions")
    print("  - Never reveals scam detection")
    print()
    print("✓ Clarification questions to keep attacker engaged")
    print("  - Varied questions per scam type")
    print("  - Calibrated urgency based on risk level")
    print("  - Keeps conversation flowing naturally")
    print()
    print("✓ Strategic engagement levels for intelligence gathering")
    print("  - deep_engagement: Critical/high phishing/financial")
    print("  - high_engagement: High risk scams")
    print("  - moderate_engagement: Medium risk scams")
    print("  - low_engagement: Low risk messages")
    print()
    print("✓ Follow-up message generation for multi-turn conversations")
    print("  - Asks progressively detailed questions")
    print("  - Maintains natural conversation flow")
    print("  - Different approaches per scam type")
    print()
    print("✓ Covert escalation responses that stall without revealing")
    print("  - Appears to comply with attacker requests")
    print("  - Actually redirects to get more information")
    print("  - Never indicates detection or suspicion")
    print()
    print("✓ Conversation pattern analysis capabilities")
    print("  - Tracks engagement level")
    print("  - Identifies attack patterns")
    print("  - Recommends actions (monitor, escalate, investigate)")
    print()
    print("="*70)

if __name__ == "__main__":
    main()
