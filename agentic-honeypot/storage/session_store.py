"""
Session storage module for agentic-honeypot
Manages in-memory session tracking with message count, intelligence extraction, and scam confirmation
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class SessionData:
    """Data class for storing individual session information"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.message_count = 0
        self.messages = []  # List of all messages in conversation
        self.extracted_intelligence = {
            'upi_ids': [],
            'phone_numbers': [],
            'urls': [],
            'suspicious_keywords': {},
        }
        self.scam_detections = []  # List of all scam detection results
        self.scam_confirmed = False  # Whether scam is definitively confirmed
        self.scam_confirmation_score = 0.0  # Cumulative confidence
        self.risk_level = 'minimal'
        self.attacker_profile = {
            'strategy': None,
            'primary_scam_type': None,
            'targets': [],  # UPI IDs, phone numbers they requested
            'payment_amount': None,
            'urls_used': [],
        }
        self.conversation_metadata = {
            'engagement_level': 'low',
            'attacker_sophistication': 'low',
            'response_patterns': [],  # How attacker responded to agent questions
        }
    
    def add_message(self, message: str, sender: str = 'attacker', role: str = 'user') -> None:
        """
        Add a message to session history
        
        Args:
            message: The message text
            sender: 'attacker' or 'agent'
            role: 'user' or 'assistant' for compatibility
        """
        self.message_count += 1
        self.messages.append({
            'timestamp': datetime.now().isoformat(),
            'sender': sender,
            'role': role,
            'message': message,
            'message_number': self.message_count,
        })
        self.last_updated = datetime.now()
    
    def add_intelligence(self, intelligence_data: Dict) -> None:
        """
        Add extracted intelligence from a message
        
        Args:
            intelligence_data: Dict with upi_ids, phone_numbers, urls, suspicious_keywords
        """
        # Merge UPI IDs
        for upi in intelligence_data.get('upi_ids', []):
            if upi not in self.extracted_intelligence['upi_ids']:
                self.extracted_intelligence['upi_ids'].append(upi)
        
        # Merge phone numbers
        for phone in intelligence_data.get('phone_numbers', []):
            if phone not in self.extracted_intelligence['phone_numbers']:
                self.extracted_intelligence['phone_numbers'].append(phone)
        
        # Merge URLs
        for url in intelligence_data.get('urls', []):
            if url not in self.extracted_intelligence['urls']:
                self.extracted_intelligence['urls'].append(url)
        
        # Merge suspicious keywords
        for category, keywords in intelligence_data.get('suspicious_keywords', {}).items():
            if category not in self.extracted_intelligence['suspicious_keywords']:
                self.extracted_intelligence['suspicious_keywords'][category] = []
            
            for keyword in keywords:
                if keyword not in self.extracted_intelligence['suspicious_keywords'][category]:
                    self.extracted_intelligence['suspicious_keywords'][category].append(keyword)
        
        self.last_updated = datetime.now()
    
    def add_scam_detection(self, detection_result: Dict) -> None:
        """
        Add a scam detection result
        
        Args:
            detection_result: Dict with is_scam, risk_score, detected_keywords, scam_type
        """
        detection = {
            'timestamp': datetime.now().isoformat(),
            'message_number': self.message_count,
            'is_scam': detection_result.get('is_scam', False),
            'risk_score': detection_result.get('risk_score', 0.0),
            'scam_type': detection_result.get('scam_type'),
            'detected_keywords': detection_result.get('detected_keywords', []),
            'reason': detection_result.get('reason'),
        }
        
        self.scam_detections.append(detection)
        self.last_updated = datetime.now()
        
        # Update risk level based on highest risk score seen
        if detection['risk_score'] > self.scam_confirmation_score:
            self.scam_confirmation_score = detection['risk_score']
        
        # Update primary scam type (most frequent)
        scam_types = [d['scam_type'] for d in self.scam_detections if d['is_scam']]
        if scam_types:
            self.attacker_profile['primary_scam_type'] = max(set(scam_types), key=scam_types.count)
        
        # Update risk level
        if self.scam_confirmation_score >= 0.85:
            self.risk_level = 'critical'
        elif self.scam_confirmation_score >= 0.65:
            self.risk_level = 'high'
        elif self.scam_confirmation_score >= 0.45:
            self.risk_level = 'medium'
        elif self.scam_confirmation_score >= 0.25:
            self.risk_level = 'low'
        else:
            self.risk_level = 'minimal'
    
    def confirm_scam(self, confidence: float = 0.95, notes: str = "") -> None:
        """
        Manually confirm that this session is a scam
        
        Args:
            confidence: Confidence level of confirmation (0.0-1.0)
            notes: Additional notes about confirmation
        """
        self.scam_confirmed = True
        self.scam_confirmation_score = max(self.scam_confirmation_score, confidence)
        if self.risk_level == 'minimal':
            self.risk_level = 'critical'
        
        # Log confirmation
        self.messages.append({
            'timestamp': datetime.now().isoformat(),
            'sender': 'system',
            'role': 'system',
            'message': f"SCAM CONFIRMED - Confidence: {confidence:.1%}, Notes: {notes}",
            'message_number': -1,
        })
        self.last_updated = datetime.now()
    
    def update_attacker_profile(self, data: Dict) -> None:
        """
        Update attacker profile information
        
        Args:
            data: Dict with strategy, targets, payment_amount, sophistication, etc.
        """
        if 'strategy' in data:
            self.attacker_profile['strategy'] = data['strategy']
        if 'targets' in data:
            self.attacker_profile['targets'] = data['targets']
        if 'payment_amount' in data:
            self.attacker_profile['payment_amount'] = data['payment_amount']
        if 'sophistication' in data:
            self.conversation_metadata['attacker_sophistication'] = data['sophistication']
        self.last_updated = datetime.now()
    
    def get_summary(self) -> Dict:
        """Get a summary of the session"""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'message_count': self.message_count,
            'scam_confirmed': self.scam_confirmed,
            'risk_level': self.risk_level,
            'scam_confirmation_score': self.scam_confirmation_score,
            'primary_scam_type': self.attacker_profile['primary_scam_type'],
            'upi_ids_found': len(self.extracted_intelligence['upi_ids']),
            'phone_numbers_found': len(self.extracted_intelligence['phone_numbers']),
            'urls_found': len(self.extracted_intelligence['urls']),
            'scam_detections_count': len([d for d in self.scam_detections if d['is_scam']]),
            'engagement_level': self.conversation_metadata['engagement_level'],
        }


class SessionStore:
    """Manages in-memory session data persistence with intelligence tracking"""
    
    def __init__(self):
        """Initialize the session store"""
        self.sessions: Dict[str, SessionData] = {}
        self.session_index: Dict[str, datetime] = {}  # For tracking session creation time
    
    def create_session(self, session_id: str) -> SessionData:
        """
        Create a new session
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            SessionData object for the new session
        """
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        session = SessionData(session_id)
        self.sessions[session_id] = session
        self.session_index[session_id] = datetime.now()
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Retrieve a session by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData if exists, None otherwise
        """
        return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, message: str, sender: str = 'attacker') -> bool:
        """
        Add a message to session
        
        Args:
            session_id: Session identifier
            message: Message text
            sender: 'attacker' or 'agent'
            
        Returns:
            True if successful, False if session not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.add_message(message, sender)
        return True
    
    def add_intelligence(self, session_id: str, intelligence_data: Dict) -> bool:
        """
        Add extracted intelligence to session
        
        Args:
            session_id: Session identifier
            intelligence_data: Intelligence extraction result
            
        Returns:
            True if successful, False if session not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.add_intelligence(intelligence_data)
        return True
    
    def add_scam_detection(self, session_id: str, detection_result: Dict) -> bool:
        """
        Add scam detection result to session
        
        Args:
            session_id: Session identifier
            detection_result: Scam detection result
            
        Returns:
            True if successful, False if session not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.add_scam_detection(detection_result)
        return True
    
    def confirm_scam(self, session_id: str, confidence: float = 0.95, notes: str = "") -> bool:
        """
        Mark session as confirmed scam
        
        Args:
            session_id: Session identifier
            confidence: Confirmation confidence
            notes: Additional notes
            
        Returns:
            True if successful, False if session not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.confirm_scam(confidence, notes)
        return True
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """
        Get session summary
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary dict if exists, None otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return session.get_summary()
    
    def get_all_sessions_summary(self) -> List[Dict]:
        """
        Get summaries of all sessions
        
        Returns:
            List of session summaries
        """
        return [session.get_summary() for session in self.sessions.values()]
    
    def get_confirmed_scams(self) -> List[Dict]:
        """
        Get all confirmed scam sessions
        
        Returns:
            List of confirmed scam session summaries
        """
        return [
            session.get_summary() 
            for session in self.sessions.values() 
            if session.scam_confirmed
        ]
    
    def get_high_risk_sessions(self, risk_level: str = 'high') -> List[Dict]:
        """
        Get sessions by risk level
        
        Args:
            risk_level: 'critical', 'high', 'medium', 'low', 'minimal'
            
        Returns:
            List of session summaries matching risk level
        """
        risk_levels = {
            'critical': ['critical'],
            'high': ['critical', 'high'],
            'medium': ['critical', 'high', 'medium'],
            'low': ['critical', 'high', 'medium', 'low'],
        }
        
        target_levels = risk_levels.get(risk_level, ['critical'])
        return [
            session.get_summary() 
            for session in self.sessions.values() 
            if session.risk_level in target_levels
        ]
    
    def get_sessions_by_scam_type(self, scam_type: str) -> List[Dict]:
        """
        Get sessions by primary scam type
        
        Args:
            scam_type: 'phishing', 'lottery', 'financial', etc.
            
        Returns:
            List of session summaries of that scam type
        """
        return [
            session.get_summary() 
            for session in self.sessions.values() 
            if session.attacker_profile.get('primary_scam_type') == scam_type
        ]
    
    def get_extracted_intelligence_summary(self) -> Dict:
        """
        Get summary of all extracted intelligence across all sessions
        
        Returns:
            Dict with aggregated intelligence
        """
        all_upi_ids = []
        all_phone_numbers = []
        all_urls = []
        all_keywords = {}
        
        for session in self.sessions.values():
            intel = session.extracted_intelligence
            
            # Aggregate UPI IDs
            for upi in intel.get('upi_ids', []):
                if isinstance(upi, dict):
                    upi_str = upi.get('upi', str(upi))
                else:
                    upi_str = str(upi)
                if upi_str not in all_upi_ids:
                    all_upi_ids.append(upi_str)
            
            # Aggregate phone numbers
            for phone in intel.get('phone_numbers', []):
                if isinstance(phone, dict):
                    phone_str = phone.get('normalized', str(phone))
                else:
                    phone_str = str(phone)
                if phone_str not in all_phone_numbers:
                    all_phone_numbers.append(phone_str)
            
            # Aggregate URLs
            for url in intel.get('urls', []):
                if isinstance(url, dict):
                    url_str = url.get('url', str(url))
                else:
                    url_str = str(url)
                if url_str not in all_urls:
                    all_urls.append(url_str)
            
            # Aggregate keywords
            for category, keywords in intel.get('suspicious_keywords', {}).items():
                if category not in all_keywords:
                    all_keywords[category] = []
                for keyword in keywords:
                    if isinstance(keyword, dict):
                        kw_str = keyword.get('keyword', str(keyword))
                    else:
                        kw_str = str(keyword)
                    if kw_str not in all_keywords[category]:
                        all_keywords[category].append(kw_str)
        
        return {
            'total_sessions': len(self.sessions),
            'confirmed_scams': len([s for s in self.sessions.values() if s.scam_confirmed]),
            'unique_upi_ids': len(all_upi_ids),
            'unique_phone_numbers': len(all_phone_numbers),
            'unique_urls': len(all_urls),
            'upi_ids': all_upi_ids[:10],  # Top 10
            'phone_numbers': all_phone_numbers[:10],
            'urls': all_urls[:10],
            'keyword_categories': list(all_keywords.keys()),
            'total_keywords_tracked': sum(len(v) for v in all_keywords.values()),
        }
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            del self.session_index[session_id]
            return True
        return False
    
    def clear_all_sessions(self) -> int:
        """
        Clear all sessions (use with caution)
        
        Returns:
            Number of sessions cleared
        """
        count = len(self.sessions)
        self.sessions.clear()
        self.session_index.clear()
        return count
