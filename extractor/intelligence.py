"""
Intelligence extraction module for agentic-honeypot
Extracts UPI IDs, phone numbers, URLs, and suspicious keywords from honeypot messages
"""

import re
from typing import Dict, List, Optional


class IntelligenceExtractor:
    """Extracts actionable intelligence from honeypot data"""
    
    # Regex patterns for different data types
    UPI_PATTERN = r'[a-zA-Z0-9._-]+@[a-zA-Z]{3,}(?:\.[a-zA-Z]{2,})?'  # e.g., username@upi
    
    PHONE_PATTERNS = {
        'india': r'(?:(?:\+91|0)?[-\s]?)?[6-9]\d{2}[-\s]?\d{3,4}[-\s]?\d{3,4}',  # Indian: +91/0 9999999999
        'international': r'\+?1?\s?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US/International
        'generic': r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,5}',  # Generic format
    }
    
    URL_PATTERN = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
    
    # Suspicious keywords for threat intelligence
    SUSPICIOUS_KEYWORDS = {
        'financial_threat': ['account', 'card', 'bank', 'payment', 'transaction', 'balance', 'credit', 'debit', 'wire transfer'],
        'urgency_markers': ['immediately', 'urgent', 'asap', 'right now', 'quickly', 'instantly', 'without delay', 'time-sensitive'],
        'credential_theft': ['verify', 'confirm', 'authenticate', 'password', 'pin', 'otp', 'credentials', 'login', 'username'],
        'social_engineering': ['trust', 'help', 'friend', 'family', 'assist', 'support', 'believe', 'understand'],
        'action_triggers': ['click', 'download', 'install', 'update', 'enable', 'allow', 'grant', 'activate', 'link'],
        'reward_baiting': ['prize', 'reward', 'won', 'claimed', 'free', 'bonus', 'win', 'lucky'],
    }
    
    def __init__(self):
        """Initialize the intelligence extractor"""
        self.extracted_data = {
            'upi_ids': [],
            'phone_numbers': [],
            'urls': [],
            'suspicious_keywords': {},
            'threat_level': 'low',
            'confidence': 0.0,
        }
    
    def extract(self, message: str) -> Dict:
        """
        Extract intelligence from raw data
        
        Args:
            message: The message to extract intelligence from
            
        Returns:
            Dictionary containing extracted UPI IDs, phone numbers, URLs, and keywords
        """
        if not message:
            return self.extracted_data
        
        # Reset extracted data
        self.extracted_data = {
            'upi_ids': [],
            'phone_numbers': [],
            'urls': [],
            'suspicious_keywords': {},
            'threat_level': 'low',
            'confidence': 0.0,
        }
        
        # Extract different data types
        self._extract_upi_ids(message)
        self._extract_phone_numbers(message)
        self._extract_urls(message)
        self._extract_suspicious_keywords(message)
        self._calculate_threat_level()
        
        return self.extracted_data
    
    def _extract_upi_ids(self, message: str) -> None:
        """
        Extract UPI IDs from message
        UPI format: username@bankname (e.g., user@okhdfcbank, merchant@okaxis)
        """
        upi_matches = re.findall(self.UPI_PATTERN, message, re.IGNORECASE)
        
        # Filter for valid UPI patterns
        valid_upis = []
        for match in upi_matches:
            # Check if it looks like a UPI ID (has @ and valid bank name parts)
            if '@' in match:
                parts = match.split('@')
                if len(parts) == 2 and len(parts[0]) > 2 and len(parts[1]) >= 3:
                    valid_upis.append({
                        'upi': match,
                        'username': parts[0],
                        'bank': parts[1],
                        'risk_score': 0.9,  # UPI IDs in messages are suspicious
                        'position': message.find(match)
                    })
        
        self.extracted_data['upi_ids'] = valid_upis
    
    def _extract_phone_numbers(self, message: str) -> None:
        """
        Extract phone numbers from message using multiple patterns
        Handles: Indian (+91-9xxx), US (+1-202), International formats
        """
        phone_numbers = []
        seen_numbers = set()  # To avoid duplicates
        
        # Try each phone pattern
        for pattern_type, pattern in self.PHONE_PATTERNS.items():
            matches = re.finditer(pattern, message, re.VERBOSE)
            
            for match in matches:
                phone = match.group(0).strip()
                
                # Normalize phone number for deduplication
                normalized = re.sub(r'[\s\-\(\)\+]', '', phone)
                
                if normalized not in seen_numbers and len(normalized) >= 10:
                    seen_numbers.add(normalized)
                    
                    # Determine region
                    region = 'India' if any(c in phone for c in ['+91', '9']) else 'International'
                    
                    phone_numbers.append({
                        'number': phone,
                        'normalized': normalized,
                        'pattern_type': pattern_type,
                        'region': region,
                        'risk_score': 0.85,  # Phone numbers in scam messages are suspicious
                        'position': match.start()
                    })
        
        self.extracted_data['phone_numbers'] = sorted(phone_numbers, key=lambda x: x['position'])
    
    def _extract_urls(self, message: str) -> None:
        """
        Extract URLs from message
        Handles: http://, https://, with and without www
        """
        url_matches = re.findall(self.URL_PATTERN, message, re.IGNORECASE)
        
        urls = []
        for url in set(url_matches):  # Remove duplicates
            # Analyze URL for suspicion indicators
            suspicion_indicators = []
            
            if 'bit.ly' in url or 'tinyurl' in url or 'shortlink' in url:
                suspicion_indicators.append('shortened_url')
            
            if 'verify' in url or 'confirm' in url or 'authenticate' in url or 'login' in url:
                suspicion_indicators.append('credential_phishing')
            
            if 'update' in url or 'urgent' in url or 'alert' in url:
                suspicion_indicators.append('urgency_trigger')
            
            # Calculate risk based on indicators
            risk_score = 0.75 + (len(suspicion_indicators) * 0.05)
            risk_score = min(risk_score, 0.99)
            
            urls.append({
                'url': url,
                'domain': self._extract_domain(url),
                'is_shortened': 'bit.ly' in url or 'tinyurl' in url,
                'suspicion_indicators': suspicion_indicators,
                'risk_score': risk_score,
                'position': message.find(url)
            })
        
        self.extracted_data['urls'] = sorted(urls, key=lambda x: x['position'])
    
    def _extract_suspicious_keywords(self, message: str) -> None:
        """
        Extract and categorize suspicious keywords from message
        Groups keywords by threat category
        """
        message_lower = message.lower()
        keyword_findings = {}
        
        for category, keywords in self.SUSPICIOUS_KEYWORDS.items():
            found_keywords = []
            
            for keyword in keywords:
                # Count occurrences with word boundaries
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.finditer(pattern, message_lower)
                
                for match in matches:
                    found_keywords.append({
                        'keyword': keyword,
                        'count': len(list(re.finditer(pattern, message_lower))),
                        'position': match.start(),
                        'risk_contribution': 0.1 + (0.05 * len(list(re.finditer(pattern, message_lower))))  # More occurrences = higher risk
                    })
            
            if found_keywords:
                # Remove duplicates and sort by position
                unique_keywords = {kw['keyword']: kw for kw in found_keywords}
                keyword_findings[category] = sorted(list(unique_keywords.values()), key=lambda x: x['position'])
        
        self.extracted_data['suspicious_keywords'] = keyword_findings
    
    def _calculate_threat_level(self) -> None:
        """
        Calculate overall threat level based on extracted indicators
        Higher scores for more dangerous combinations
        """
        confidence = 0.0
        
        # UPI IDs in messages = high threat
        if self.extracted_data['upi_ids']:
            confidence += 0.25
        
        # Phone numbers in messages = medium threat
        if self.extracted_data['phone_numbers']:
            confidence += 0.20
        
        # URLs in messages = medium threat
        if self.extracted_data['urls']:
            confidence += 0.20
        
        # Suspicious keywords boost
        keyword_categories_found = len(self.extracted_data['suspicious_keywords'])
        confidence += (keyword_categories_found * 0.10)
        
        # Specific combinations increase threat level
        if self.extracted_data['upi_ids'] and self.extracted_data['phone_numbers']:
            confidence += 0.15  # Asking for payment + contact info = high threat
        
        if 'credential_theft' in self.extracted_data['suspicious_keywords'] and self.extracted_data['urls']:
            confidence += 0.10  # Asking for credentials + URL = phishing
        
        if 'urgency_markers' in self.extracted_data['suspicious_keywords']:
            confidence += 0.05  # Urgency adds pressure
        
        # Cap confidence at 1.0
        self.extracted_data['confidence'] = min(confidence, 1.0)
        
        # Determine threat level
        if self.extracted_data['confidence'] >= 0.85:
            self.extracted_data['threat_level'] = 'critical'
        elif self.extracted_data['confidence'] >= 0.65:
            self.extracted_data['threat_level'] = 'high'
        elif self.extracted_data['confidence'] >= 0.45:
            self.extracted_data['threat_level'] = 'medium'
        elif self.extracted_data['confidence'] >= 0.25:
            self.extracted_data['threat_level'] = 'low'
        else:
            self.extracted_data['threat_level'] = 'minimal'
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            # Remove protocol
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            # Remove www
            domain = domain.replace('www.', '')
            return domain
        except:
            return url
    
    def get_summary(self) -> str:
        """Get a human-readable summary of extracted intelligence"""
        summary_parts = []
        
        if self.extracted_data['upi_ids']:
            summary_parts.append(f"🏦 Found {len(self.extracted_data['upi_ids'])} UPI ID(s)")
        
        if self.extracted_data['phone_numbers']:
            summary_parts.append(f"📱 Found {len(self.extracted_data['phone_numbers'])} phone number(s)")
        
        if self.extracted_data['urls']:
            summary_parts.append(f"🔗 Found {len(self.extracted_data['urls'])} URL(s)")
        
        if self.extracted_data['suspicious_keywords']:
            total_keywords = sum(len(v) for v in self.extracted_data['suspicious_keywords'].values())
            summary_parts.append(f"⚠️ Found {total_keywords} suspicious keyword(s)")
        
        summary_parts.append(f"🎯 Threat Level: {self.extracted_data['threat_level'].upper()} ({self.extracted_data['confidence']:.1%})")
        
        return " | ".join(summary_parts) if summary_parts else "✓ No suspicious indicators found"
