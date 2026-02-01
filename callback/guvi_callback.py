"""
Callback handler for GUVI integration in agentic-honeypot
Sends final extracted intelligence and scam confirmation to GUVI endpoint
"""

import requests
import json
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging
from config import GUVI_ENDPOINT, GUVI_API_KEY, GUVI_TIMEOUT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GuviCallback:
    """Handles callbacks and integrations with GUVI for threat intelligence sharing"""
    
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 10):
        """
        Initialize GUVI callback handler
        
        Args:
            endpoint: GUVI endpoint URL (defaults to config)
            api_key: GUVI API key (defaults to config)
            timeout: Request timeout in seconds (default: 10)
        """
        self.endpoint = endpoint or GUVI_ENDPOINT or "https://guvi.example.com/api/v1/intelligence"
        self.api_key = api_key or GUVI_API_KEY or "default-api-key"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Agentic-Honeypot/1.0',
        })
    
    def send_intelligence(self, session_data: Dict) -> Tuple[bool, Dict]:
        """
        Send extracted intelligence to GUVI endpoint
        
        Args:
            session_data: Complete session data with intelligence
            
        Returns:
            Tuple of (success: bool, response: dict)
        """
        try:
            # Build the payload
            payload = self._build_payload(session_data)
            
            # Validate payload
            if not self._validate_payload(payload):
                logger.error(f"Invalid payload for session {session_data.get('session_id')}")
                return False, {'error': 'Payload validation failed'}
            
            # Send to GUVI endpoint
            response = self._send_request(payload)
            
            if response['success']:
                logger.info(f"Successfully sent intelligence for session {session_data.get('session_id')} to GUVI")
                return True, response
            else:
                logger.warning(f"GUVI endpoint returned error: {response.get('message')}")
                return False, response
                
        except Exception as e:
            logger.error(f"Error sending intelligence to GUVI: {str(e)}")
            return False, {'error': str(e), 'error_type': type(e).__name__}
    
    def _build_payload(self, session_data: Dict) -> Dict:
        """
        Build payload exactly as specified for GUVI endpoint
        
        Args:
            session_data: Session object or dict with session information
            
        Returns:
            Payload dict formatted for GUVI
        """
        # Handle both SessionData objects and dictionaries
        if hasattr(session_data, '__dict__') and hasattr(session_data, 'session_id'):
            # This is a SessionData object
            session_dict = self._convert_session_object_to_dict(session_data)
        else:
            # This is already a dict
            session_dict = session_data
        
        session_id = session_dict.get('session_id', 'unknown')
        
        # Build threat intelligence payload
        payload = {
            # Metadata
            'report_id': self._generate_report_id(session_id),
            'timestamp': datetime.now().isoformat(),
            'source': 'agentic-honeypot',
            'version': '1.0',
            
            # Session Information
            'session': {
                'session_id': session_id,
                'created_at': session_dict.get('created_at'),
                'ended_at': datetime.now().isoformat(),
                'duration_seconds': self._calculate_duration(session_dict.get('created_at')),
                'message_count': session_dict.get('message_count', 0),
                'conversation_history': session_dict.get('messages', []),
            },
            
            # Threat Classification
            'threat': {
                'is_scam': session_dict.get('scam_confirmed', False),
                'scam_type': session_dict.get('primary_scam_type'),
                'risk_level': session_dict.get('risk_level', 'unknown'),
                'confidence_score': session_dict.get('scam_confirmation_score', 0.0),
                'scam_detections': session_dict.get('scam_detections', []),
            },
            
            # Extracted Intelligence - IOCs (Indicators of Compromise)
            'indicators_of_compromise': {
                'upi_ids': session_dict.get('upi_ids', []),
                'phone_numbers': session_dict.get('phone_numbers', []),
                'urls': session_dict.get('urls', []),
                'domains': self._extract_domains(session_dict.get('urls', [])),
                'email_addresses': self._extract_emails(session_dict.get('upi_ids', [])),
            },
            
            # Suspicious Keywords
            'keywords': session_dict.get('suspicious_keywords', {}),
            
            # Attacker Profile
            'attacker_profile': {
                'strategy': session_dict.get('strategy'),
                'targets': session_dict.get('targets', []),
                'payment_amount': session_dict.get('payment_amount'),
                'sophistication_level': session_dict.get('attacker_sophistication', 'unknown'),
                'engagement_level': session_dict.get('engagement_level', 'unknown'),
            },
            
            # Detection Results
            'detection_analysis': {
                'total_detections': len(session_dict.get('scam_detections', [])),
                'confirmed_scam_detections': len([d for d in session_dict.get('scam_detections', []) if d.get('is_scam')]),
                'average_risk_score': self._calculate_average_risk(session_dict.get('scam_detections', [])),
                'detection_keywords': self._extract_all_keywords(session_dict.get('scam_detections', [])),
            },
            
            # Metadata
            'metadata': {
                'honeypot_instance': 'agentic-honeypot-001',
                'deployment_region': 'global',
                'tags': self._generate_tags(session_dict),
            }
        }
        
        return payload
    
    def _send_request(self, payload: Dict) -> Dict:
        """
        Send HTTP request to GUVI endpoint with timeout and error handling
        
        Args:
            payload: Payload to send
            
        Returns:
            Response dict with success status and data
        """
        try:
            # Log request (without sensitive data in logs)
            logger.debug(f"Sending request to {self.endpoint}")
            
            # Send POST request with timeout
            response = self.session.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout,
                verify=True,  # Verify SSL certificates
            )
            
            # Handle response
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return {
                        'success': True,
                        'status_code': response.status_code,
                        'message': 'Intelligence successfully sent to GUVI',
                        'response': response_data,
                    }
                except json.JSONDecodeError:
                    return {
                        'success': True,
                        'status_code': response.status_code,
                        'message': 'Intelligence sent but response JSON parsing failed',
                        'response_text': response.text[:500],  # First 500 chars
                    }
            
            elif response.status_code == 401:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'message': 'Authentication failed - check GUVI API key',
                    'error': 'Unauthorized',
                }
            
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    return {
                        'success': False,
                        'status_code': response.status_code,
                        'message': 'Invalid request payload',
                        'error': error_data.get('error', 'Bad Request'),
                        'details': error_data.get('details'),
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'status_code': response.status_code,
                        'message': 'Invalid request payload',
                        'error': response.text[:200],
                    }
            
            elif response.status_code == 429:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'message': 'Rate limited - too many requests',
                    'retry_after': response.headers.get('Retry-After', 'unknown'),
                }
            
            elif response.status_code == 503:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'message': 'GUVI service temporarily unavailable',
                }
            
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'message': f'Unexpected status code: {response.status_code}',
                    'response': response.text[:200],
                }
        
        except requests.Timeout:
            logger.error(f"Request timeout after {self.timeout} seconds")
            return {
                'success': False,
                'error': 'Timeout',
                'message': f'Request timed out after {self.timeout} seconds',
                'timeout_seconds': self.timeout,
            }
        
        except requests.ConnectionError as e:
            logger.error(f"Connection error to {self.endpoint}: {str(e)}")
            return {
                'success': False,
                'error': 'ConnectionError',
                'message': f'Failed to connect to GUVI endpoint: {str(e)}',
                'endpoint': self.endpoint,
            }
        
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {
                'success': False,
                'error': 'RequestException',
                'message': f'Request failed: {str(e)}',
            }
    
    def _validate_payload(self, payload: Dict) -> bool:
        """
        Validate payload structure before sending
        
        Args:
            payload: Payload to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['report_id', 'timestamp', 'source', 'session', 'threat', 'indicators_of_compromise']
        
        for field in required_fields:
            if field not in payload:
                logger.warning(f"Missing required field in payload: {field}")
                return False
        
        # Validate session structure
        session = payload.get('session', {})
        if 'session_id' not in session:
            logger.warning("Missing session_id in payload")
            return False
        
        # Validate threat structure
        threat = payload.get('threat', {})
        if 'risk_level' not in threat:
            logger.warning("Missing risk_level in threat")
            return False
        
        return True
    
    @staticmethod
    def _convert_session_object_to_dict(session_obj) -> Dict:
        """
        Convert SessionData object to dictionary
        
        Args:
            session_obj: SessionData object
            
        Returns:
            Dictionary representation
        """
        return {
            'session_id': session_obj.session_id,
            'created_at': session_obj.created_at.isoformat() if hasattr(session_obj.created_at, 'isoformat') else str(session_obj.created_at),
            'message_count': session_obj.message_count,
            'messages': session_obj.messages,
            'scam_confirmed': session_obj.scam_confirmed,
            'scam_confirmation_score': session_obj.scam_confirmation_score,
            'risk_level': session_obj.risk_level,
            'primary_scam_type': session_obj.attacker_profile.get('primary_scam_type'),
            'strategy': session_obj.attacker_profile.get('strategy'),
            'targets': session_obj.attacker_profile.get('targets', []),
            'payment_amount': session_obj.attacker_profile.get('payment_amount'),
            'attacker_sophistication': session_obj.conversation_metadata.get('attacker_sophistication'),
            'engagement_level': session_obj.conversation_metadata.get('engagement_level'),
            'scam_detections': session_obj.scam_detections,
            'upi_ids': session_obj.extracted_intelligence.get('upi_ids', []),
            'phone_numbers': session_obj.extracted_intelligence.get('phone_numbers', []),
            'urls': session_obj.extracted_intelligence.get('urls', []),
            'suspicious_keywords': session_obj.extracted_intelligence.get('suspicious_keywords', {}),
        }
    
    @staticmethod
    def _generate_report_id(session_id: str) -> str:
        """Generate unique report ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
        return f"REPORT-{session_id}-{timestamp}"
    
    @staticmethod
    def _calculate_duration(created_at: str) -> int:
        """Calculate session duration in seconds"""
        try:
            if isinstance(created_at, str):
                created_dt = datetime.fromisoformat(created_at)
            else:
                created_dt = created_at
            duration = (datetime.now() - created_dt).total_seconds()
            return int(duration)
        except:
            return 0
    
    @staticmethod
    def _extract_domains(urls: list) -> list:
        """Extract unique domains from URLs"""
        domains = set()
        for url in urls:
            if isinstance(url, dict):
                domain = url.get('domain', '')
            else:
                domain = str(url)
            if domain:
                domains.add(domain)
        return list(domains)
    
    @staticmethod
    def _extract_emails(upi_ids: list) -> list:
        """Extract email-like identifiers from UPI IDs"""
        emails = []
        for upi in upi_ids:
            if isinstance(upi, dict):
                upi_str = upi.get('upi', '')
            else:
                upi_str = str(upi)
            if '@' in upi_str:
                emails.append(upi_str)
        return list(set(emails))
    
    @staticmethod
    def _calculate_average_risk(detections: list) -> float:
        """Calculate average risk score from detections"""
        if not detections:
            return 0.0
        risk_scores = [d.get('risk_score', 0.0) for d in detections if d.get('is_scam')]
        if not risk_scores:
            return 0.0
        return round(sum(risk_scores) / len(risk_scores), 3)
    
    @staticmethod
    def _extract_all_keywords(detections: list) -> list:
        """Extract all unique keywords from detections"""
        keywords = set()
        for detection in detections:
            for keyword in detection.get('detected_keywords', []):
                keywords.add(keyword)
        return list(keywords)
    
    @staticmethod
    def _generate_tags(session_dict: Dict) -> list:
        """Generate tags for the threat intelligence report"""
        tags = []
        
        # Add scam type tag
        scam_type = session_dict.get('primary_scam_type')
        if scam_type:
            tags.append(f"scam:{scam_type}")
        
        # Add risk level tag
        risk_level = session_dict.get('risk_level', 'unknown')
        tags.append(f"risk:{risk_level}")
        
        # Add IOC tags
        if session_dict.get('upi_ids'):
            tags.append('ioc:upi')
        if session_dict.get('phone_numbers'):
            tags.append('ioc:phone')
        if session_dict.get('urls'):
            tags.append('ioc:url')
        
        # Add engagement level tag
        engagement = session_dict.get('engagement_level', 'unknown')
        tags.append(f"engagement:{engagement}")
        
        return tags
