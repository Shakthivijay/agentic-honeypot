"""
Scam detection module for agentic-honeypot
"""

from config import SCAM_CONFIDENCE_THRESHOLD
from typing import Dict, List, Tuple


class ScamDetector:
    """Detects and identifies scam patterns and threats"""
    
    def __init__(self):
        """Initialize the scam detector with risk-scored keywords"""
        # Keywords mapped to risk scores (0.0-1.0)
        # Higher score = more indicative of scam
        self.scam_keywords_with_scores: Dict[str, float] = {
            # Phishing keywords (HIGH RISK)
            "verify account": 0.95,
            "confirm identity": 0.95,
            "verify email": 0.90,
            "confirm password": 0.95,
            "validate account": 0.90,
            "verify information": 0.85,
            
            # Urgency keywords (HIGH RISK)
            "urgent": 0.85,
            "immediately": 0.80,
            "act now": 0.85,
            "limited time": 0.75,
            "expires": 0.80,
            "right now": 0.75,
            "asap": 0.75,
            
            # Financial keywords (HIGH RISK)
            "update payment": 0.90,
            "payment information": 0.88,
            "credit card": 0.85,
            "banking details": 0.90,
            "account number": 0.88,
            "transfer money": 0.92,
            "wire funds": 0.92,
            
            # Lottery/Prize keywords (MEDIUM-HIGH RISK)
            "claim prize": 0.90,
            "won lottery": 0.92,
            "congratulations": 0.70,
            "prize": 0.75,
            "claim reward": 0.85,
            "collect money": 0.80,
            
            # Click/Action keywords (MEDIUM RISK)
            "click here": 0.65,
            "click link": 0.70,
            "open link": 0.65,
            "confirm here": 0.75,
            "download": 0.60,
            
            # Threat keywords (HIGH RISK)
            "account locked": 0.85,
            "suspended": 0.80,
            "disabled": 0.75,
            "compromised": 0.90,
            "unauthorized access": 0.88,
            "security alert": 0.80,
            
            # Social engineering (MEDIUM RISK)
            "help": 0.40,
            "support": 0.35,
            "call us": 0.50,
            "contact": 0.40,
            "dear customer": 0.60,
            "dear user": 0.55,
        }
        
        self.confidence_threshold = SCAM_CONFIDENCE_THRESHOLD
    
    def _analyze_keywords(self, message: str) -> Tuple[List[Dict], float]:
        """
        Analyze message text for scam keywords and calculate risk score.
        
        Args:
            message: The message text to analyze
            
        Returns:
            Tuple of (detected_keywords_list, total_risk_score)
            detected_keywords_list: List of dicts with keyword, score, and count
            total_risk_score: Aggregated risk score (0.0-1.0)
        """
        message_lower = message.lower()
        detected_keywords = []
        total_risk = 0.0
        
        # Analyze each keyword
        for keyword, risk_score in self.scam_keywords_with_scores.items():
            # Count occurrences of keyword
            count = message_lower.count(keyword)
            
            if count > 0:
                # Calculate risk contribution (score * occurrence factor)
                # Multiple occurrences increase risk
                occurrence_multiplier = min(1.0 + (count - 1) * 0.15, 1.8)
                risk_contribution = risk_score * occurrence_multiplier
                total_risk += risk_contribution
                
                detected_keywords.append({
                    "keyword": keyword,
                    "risk_score": risk_score,
                    "occurrences": count,
                    "contribution": round(risk_contribution, 3)
                })
        
        # Normalize total risk score to 0.0-1.0 range
        # Use a more aggressive normalization for better sensitivity
        if len(detected_keywords) > 0:
            # Calculate average risk across keywords
            average_risk = total_risk / len(detected_keywords)
            # Apply slight boost for multiple keywords
            keyword_count_boost = min(1.0 + (len(detected_keywords) - 1) * 0.05, 1.5)
            normalized_score = min(average_risk * keyword_count_boost, 1.0)
        else:
            normalized_score = 0.0
        
        # Sort keywords by risk contribution (highest first)
        detected_keywords.sort(key=lambda x: x["contribution"], reverse=True)
        
        return detected_keywords, normalized_score
    
    def _determine_scam_type(self, message: str, detected_keywords: List[Dict]) -> str:
        """
        Determine the type of scam based on detected keywords.
        
        Args:
            message: The message text
            detected_keywords: List of detected keywords
            
        Returns:
            scam_type: Classification of the scam type
        """
        message_lower = message.lower()
        keyword_texts = [kw["keyword"] for kw in detected_keywords]
        keyword_string = " ".join(keyword_texts)
        
        # Phishing indicators
        if any(kw in keyword_string for kw in ["verify", "confirm", "validate", "account", "password"]):
            return "phishing"
        
        # Lottery/Prize indicators
        elif any(kw in keyword_string for kw in ["prize", "claim", "won", "lottery", "reward"]):
            return "lottery"
        
        # Financial scam indicators
        elif any(kw in keyword_string for kw in ["payment", "credit card", "banking", "transfer", "wire"]):
            return "financial"
        
        # Account threat indicators
        elif any(kw in keyword_string for kw in ["locked", "suspended", "disabled", "compromised"]):
            return "account_threat"
        
        # Default to social engineering
        else:
            return "social_engineering"
    
    def detect(self, message: str) -> dict:
        """
        Detect scams in provided message data using risk scoring.
        
        Returns:
            dict: {
                'is_scam': bool,
                'confidence': float (0.0-1.0),
                'risk_score': float (0.0-1.0),
                'scam_type': str or None,
                'detected_keywords': list of detected keywords with scores,
                'reason': str
            }
        """
        if not message:
            return {
                "is_scam": False,
                "confidence": 0.0,
                "risk_score": 0.0,
                "scam_type": None,
                "detected_keywords": [],
                "reason": "Empty message"
            }
        
        # Analyze keywords and calculate risk score
        detected_keywords, risk_score = self._analyze_keywords(message)
        
        # Determine if it's a scam based on threshold
        is_scam = risk_score >= self.confidence_threshold
        
        # Determine scam type
        scam_type = None
        if is_scam and detected_keywords:
            scam_type = self._determine_scam_type(message, detected_keywords)
        
        return {
            "is_scam": is_scam,
            "confidence": risk_score,
            "risk_score": round(risk_score, 3),
            "scam_type": scam_type,
            "detected_keywords": detected_keywords,
            "reason": f"Detected {len(detected_keywords)} scam indicators with risk score: {round(risk_score, 3)}"
        }
