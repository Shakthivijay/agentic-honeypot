"""
Agent brain logic for agentic-honeypot with intelligent, human-like responses
"""

import random
from config import AGENT_MODEL, AGENT_TIMEOUT
from typing import Dict, List


class AgentBrain:
    """
    Core AI agent logic for honeypot operations.
    
    Maintains human-like engagement while gathering intelligence.
    Never reveals scam detection to keep attacker engaged.
    """
    
    def __init__(self):
        """Initialize the agent brain with response templates"""
        self.model = AGENT_MODEL
        self.timeout = AGENT_TIMEOUT
        
        # Human-like greeting responses (covert operation)
        self.greetings = [
            "Hi there! How are you doing today?",
            "Hello! Thanks for reaching out. What can I help with?",
            "Hey! I'm here to help. What's on your mind?",
            "Hi! Nice to hear from you. What brings you here?",
            "Hello! I'm happy to assist you. What's going on?",
        ]
        
        # Clarification questions to gather more info and keep engaged
        self.clarification_questions = {
            "phishing": [
                "Could you tell me more about this message? Where did you receive it from?",
                "I want to make sure I understand. Can you walk me through what happened?",
                "This is interesting. Have you seen similar messages before?",
                "Do you remember when you first received this? Can you share the details?",
                "Can you describe the sender's address or where this came from?",
            ],
            "lottery": [
                "Wow, congratulations! Can you share more details about this offer?",
                "That sounds exciting! How did you find out about this opportunity?",
                "I'd love to hear more. What exactly were you asked to do?",
                "Can you tell me step by step how you learned about this?",
                "What's the next step they mentioned in the process?",
            ],
            "financial": [
                "I see. Could you explain what kind of payment they were requesting?",
                "Can you share more about your account status? I want to help.",
                "What made you concerned about this payment request?",
                "Do you have any documentation about this request?",
                "How urgently did they say this needed to happen?",
            ],
            "account_threat": [
                "I understand your concern. Can you tell me what the alert said exactly?",
                "Where did you see this security message?",
                "Have you noticed anything unusual on your account?",
                "What actions were they asking you to take?",
                "Did they ask for any information to 'verify' your account?",
            ],
            "social_engineering": [
                "I appreciate you sharing this. Can you give me more context?",
                "What exactly are they trying to get you to do?",
                "How did this conversation start?",
                "Can you tell me their story? What's their angle?",
            ]
        }
        
        # Risk-based response templates (calibrated by risk level)
        self.responses = {
            "phishing": {
                "critical": "Thanks for sharing this. These kinds of messages can be tricky. Can you tell me exactly what they're asking you to do?",
                "high": "I appreciate you letting me know about this. I have a few questions to help understand better. What exactly did they ask you for?",
                "medium": "Interesting. I'd like to learn more about this to see how I can assist you.",
                "low": "That's something new. Can you tell me what's happening here?"
            },
            "lottery": {
                "critical": "That sounds amazing! I'd love to help you with this. Could you tell me step by step what happened?",
                "high": "Wow! That's quite an opportunity. What specifically were they asking you to do next?",
                "medium": "That's exciting news. Can you walk me through the details of this offer?",
                "low": "Interesting! Tell me more about what you just found out."
            },
            "financial": {
                "critical": "I see. This sounds urgent. Can you explain exactly what they're asking for?",
                "high": "I understand you're concerned. Can you tell me more about the payment request?",
                "medium": "I want to help clarify this situation. What are they requesting from you?",
                "low": "What's happening with your account?"
            },
            "account_threat": {
                "critical": "That must be concerning. Can you tell me what the alert said and where you saw it?",
                "high": "I understand your worry. What specific threat did they mention?",
                "medium": "Security alerts can be confusing. Can you explain what happened?",
                "low": "Tell me about this security message you got."
            },
            "social_engineering": {
                "critical": "That's an interesting situation. Can you tell me more about this interaction?",
                "high": "I'd like to understand this better. What are they trying to get you to do?",
                "medium": "Can you share more details about this message?",
                "low": "What's going on with this conversation?"
            },
        }
    
    def process(self, data: dict) -> dict:
        """
        Process detected scam and generate intelligent, human-like agent response.
        
        Args:
            data: {
                'message': str,
                'scam_type': str,
                'risk_score': float (0.0-1.0),
                'detected_keywords': list (optional),
                'source': str (optional),
                'metadata': dict (optional)
            }
        
        Returns:
            dict: {
                'reply': str,
                'action': str,
                'confidence': float,
                'engagement_level': str,
                'strategy': str,
                'scam_type': str,
                'risk_level': str
            }
        """
        if not data:
            return {
                "reply": "Sorry, I didn't catch that. Could you say that again?",
                "action": "error",
                "confidence": 0.0,
                "engagement_level": "neutral",
                "strategy": "error_recovery",
                "scam_type": None,
                "risk_level": "unknown"
            }
        
        message = data.get("message", "")
        scam_type = data.get("scam_type", "social_engineering")
        risk_score = data.get("risk_score", 0.5)
        detected_keywords = data.get("detected_keywords", [])
        
        # Determine risk level for response calibration
        risk_level = self._categorize_risk(risk_score)
        
        # Generate human-like, intelligent response (NEVER reveal detection)
        reply = self._generate_intelligent_reply(scam_type, risk_level, detected_keywords)
        
        # Determine action (covert - never reveal in response)
        action = self._determine_action(scam_type, risk_score)
        
        # Calculate engagement strategy
        engagement_level = self._calculate_engagement(risk_score, scam_type)
        strategy = self._determine_strategy(scam_type, risk_score)
        
        return {
            "reply": reply,
            "action": action,
            "confidence": round(risk_score, 3),
            "scam_type": scam_type,
            "engagement_level": engagement_level,
            "strategy": strategy,
            "keywords_detected": len(detected_keywords),
            "risk_level": risk_level
        }
    
    def _categorize_risk(self, risk_score: float) -> str:
        """
        Categorize risk score into human-readable levels.
        
        Returns:
            'critical', 'high', 'medium', or 'low'
        """
        if risk_score >= 0.85:
            return "critical"
        elif risk_score >= 0.75:
            return "high"
        elif risk_score >= 0.65:
            return "medium"
        else:
            return "low"
    
    def _generate_intelligent_reply(self, scam_type: str, risk_level: str, detected_keywords: List[Dict]) -> str:
        """
        Generate human-like response that appears helpful and interested.
        
        Strategy:
        - Never reveal scam detection
        - Show genuine interest and empathy
        - Ask clarifying questions to keep engaged
        - Maintain natural, conversational tone
        - Calibrate urgency/enthusiasm based on risk level
        """
        # Get appropriate response based on scam type and risk level
        responses = self.responses.get(scam_type, self.responses["social_engineering"])
        base_reply = responses.get(risk_level, responses.get("medium", "I appreciate you reaching out. Can you tell me more?"))
        
        # Get clarification question for continued engagement
        clarifications = self.clarification_questions.get(scam_type, [])
        question = random.choice(clarifications) if clarifications else "Could you tell me more about this?"
        
        # Combine into natural, human-like response
        if risk_level == "critical":
            # High risk: Show urgency and concern to keep very engaged
            reply = f"{base_reply}\n\n{question}"
        elif risk_level == "high":
            # High risk: Show genuine interest
            reply = f"{base_reply} {question}"
        elif risk_level == "medium":
            # Medium risk: Casual interest
            reply = f"{base_reply} {question}"
        else:
            # Low risk: Minimal engagement
            reply = f"{base_reply} {question}"
        
        return reply
    
    def _determine_action(self, scam_type: str, risk_score: float) -> str:
        """
        Determine backend action based on scam type and risk score.
        
        Actions are INTERNAL ONLY - never shared with attacker.
        """
        if risk_score >= 0.85:
            actions = {
                "phishing": "quarantine_and_deep_log",
                "lottery": "block_and_alert_authorities",
                "financial": "flag_critical_investigate",
                "account_threat": "critical_security_alert",
                "social_engineering": "deep_monitor_and_log"
            }
        elif risk_score >= 0.75:
            actions = {
                "phishing": "quarantine_and_log",
                "lottery": "block_and_flag",
                "financial": "flag_and_investigate",
                "account_threat": "security_alert",
                "social_engineering": "monitor_and_log"
            }
        elif risk_score >= 0.65:
            actions = {
                "phishing": "monitor_and_log",
                "lottery": "flag_for_review",
                "financial": "investigate_and_log",
                "account_threat": "log_alert",
                "social_engineering": "log_conversation"
            }
        else:
            actions = {
                "phishing": "log",
                "lottery": "log",
                "financial": "log",
                "account_threat": "log",
                "social_engineering": "log"
            }
        
        return actions.get(scam_type, "log")
    
    def _calculate_engagement(self, risk_score: float, scam_type: str) -> str:
        """
        Calculate engagement level to keep attacker engaged longer.
        
        Higher engagement = More time for intelligence gathering.
        """
        if risk_score >= 0.85:
            if scam_type in ["phishing", "financial"]:
                return "deep_engagement"  # Keep very engaged for critical intel
            else:
                return "high_engagement"
        elif risk_score >= 0.75:
            return "high_engagement"
        elif risk_score >= 0.65:
            return "moderate_engagement"
        else:
            return "low_engagement"
    
    def _determine_strategy(self, scam_type: str, risk_score: float) -> str:
        """
        Determine operational strategy for handling interaction.
        
        Strategies:
        - intelligence_gathering: Ask questions, learn attack patterns
        - stall_and_observe: Keep engaged without committing
        - deep_investigation: Analyze attack methodology
        - contain: Prevent escalation
        - monitor_only: Passive logging
        """
        if risk_score >= 0.85:
            return "intelligence_gathering"  # High priority for learning
        elif risk_score >= 0.75:
            if scam_type in ["phishing", "financial"]:
                return "deep_investigation"
            else:
                return "intelligence_gathering"
        elif risk_score >= 0.65:
            return "stall_and_observe"
        else:
            return "monitor_only"
    
    def craft_follow_up(self, previous_message: str, scam_type: str, risk_score: float) -> str:
        """
        Craft intelligent follow-up messages for multi-turn conversations.
        
        Used to maintain engagement and gather more intelligence about attacker methods.
        """
        risk_level = self._categorize_risk(risk_score)
        
        follow_ups = {
            "phishing": {
                "critical": [
                    "I understand your concern. Can you tell me the exact link or sender's email?",
                    "That's concerning. Did you click on anything or enter any information?",
                    "I want to protect you. Can you describe exactly what they asked for?",
                    "This is important. Did they ask for passwords or login details?",
                ],
                "high": [
                    "That sounds important. What's the link they provided?",
                    "Did you share any personal information? I want to help.",
                    "Can you forward me the exact message? I'd like to review it.",
                    "What email address did this come from?",
                ],
                "medium": [
                    "Thanks for the details. What's your next step going to be?",
                    "Have you checked if this is legitimate?",
                    "Do you want to go ahead with what they asked?",
                ],
            },
            "lottery": {
                "critical": [
                    "This is amazing! Do you know what the prize process is?",
                    "How much would you need to pay to claim this?",
                    "What's the next step they want you to take?",
                    "Are you ready to claim your prize? What do they need?",
                ],
                "high": [
                    "This sounds like a great opportunity! Are you going to pursue it?",
                    "What do they need from you to proceed?",
                    "When can you expect more details?",
                    "What documentation did they send you?",
                ],
                "medium": [
                    "That's exciting! Will you follow up with them?",
                    "What happens next in the process?",
                ],
            },
            "financial": {
                "critical": [
                    "I understand. How much are they asking you to transfer?",
                    "What's the reason they gave for the urgent payment?",
                    "Which payment method would you use?",
                    "Did they specify an account number or banking details?",
                ],
                "high": [
                    "That must be stressful. What exactly do they need?",
                    "How soon do they need the payment?",
                    "Have you prepared to make the payment?",
                    "What account are they asking you to send money to?",
                ],
                "medium": [
                    "What's your plan at this point?",
                    "Are you considering their request?",
                ],
            },
        }
        
        scam_responses = follow_ups.get(scam_type, {})
        level_responses = scam_responses.get(risk_level, [])
        
        if level_responses:
            return random.choice(level_responses)
        else:
            return "Can you tell me more about what's happening?"
    
    def analyze_conversation_pattern(self, conversation_history: List[str]) -> Dict:
        """
        Analyze conversation patterns to understand attacker behavior and intent.
        
        Returns:
            Analysis of conversation patterns and recommended actions
        """
        return {
            "turn_count": len(conversation_history),
            "user_engagement": "high" if len(conversation_history) > 2 else "low",
            "pattern_identified": "potential_social_engineering" if len(conversation_history) > 4 else "unknown",
            "recommended_action": "continue_monitoring" if len(conversation_history) <= 5 else "escalate_investigation",
            "attacker_persistence": "high" if len(conversation_history) > 6 else "standard"
        }
    
    def get_covert_response_for_escalation(self, scam_type: str, risk_score: float) -> str:
        """
        Generate a response that appears to comply with attacker's request
        while actually stalling or redirecting.
        
        Used when attacker becomes impatient or pushes for action.
        """
        risk_level = self._categorize_risk(risk_score)
        
        covert_responses = {
            "phishing": {
                "critical": "I want to help, but I need to verify something first. Can you explain this more?",
                "high": "I'm interested but need to be careful. Can you walk me through exactly what happens?",
                "medium": "I appreciate the help. Before I proceed, can you confirm a few details?"
            },
            "financial": {
                "critical": "I'm ready to help. Let me just verify a few things before we proceed. Can you confirm the account details again?",
                "high": "I want to make sure I do this right. Can you walk me through the process one more time?",
                "medium": "I'm considering it. Can you give me a bit more time to arrange things?"
            },
            "lottery": {
                "critical": "I'm excited about this! Just to be thorough, can you explain the verification process one more time?",
                "high": "This is great news. Can you confirm all the requirements one more time before I proceed?",
                "medium": "I'm looking into it. Can you send me more documentation about the process?"
            },
        }
        
        response_dict = covert_responses.get(scam_type, {})
        return response_dict.get(risk_level, "I appreciate your patience. Let me gather some information and get back to you.")
