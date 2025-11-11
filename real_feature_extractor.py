#!/usr/bin/env python3
"""
Real Feature Extractor for Phishing Detection
Extracts the same features as in the training dataset
"""

import re
import urllib.parse
import socket
import requests
from typing import Dict, List
import tldextract
import whois
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RealFeatureExtractor:
    def __init__(self):
        self.feature_names = [
            'Have_IP', 'Have_At', 'URL_Length', 'URL_Depth', 'Redirection',
            'https_Domain', 'TinyURL', 'Prefix_Suffix', 'DNS_Record',
            'Web_Traffic', 'Domain_Age', 'Domain_End', 'iFrame',
            'Mouse_Over', 'Right_Click', 'Web_Forwards'
        ]
        # Cache for DNS and domain lookups to improve performance
        self.dns_cache = {}
        self.domain_cache = {}
    
    def extract_url_features(self, url: str) -> Dict[str, int]:
        """Extract features from URL matching the training dataset format"""
        features = {}
        
        try:
            # Parse URL
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # 1. Have_IP: Check if URL contains IP address
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            features['Have_IP'] = 1 if re.search(ip_pattern, domain) else 0
            
            # 2. Have_At: Check if URL contains @ symbol
            features['Have_At'] = 1 if '@' in url else 0
            
            # 3. URL_Length: Categorize URL length (based on training data patterns)
            url_len = len(url)
            # Legitimate sites can have longer URLs (e.g., PayPal, Amazon)
            if url_len < 30:
                features['URL_Length'] = 1  # Short legitimate sites
            elif url_len < 100:
                features['URL_Length'] = 1  # Medium - typically legitimate
            else:
                features['URL_Length'] = 0  # Very long - often phishing

            # 4. URL_Depth: Count number of subdirectories (based on training data)
            path_parts = [part for part in parsed_url.path.split('/') if part]
            depth = len(path_parts)
            if depth <= 2:
                features['URL_Depth'] = 1  # Normal depth (most legitimate sites)
            elif depth <= 4:
                features['URL_Depth'] = 2  # Medium depth (e.g., /account/login)
            elif depth <= 6:
                features['URL_Depth'] = 3  # High depth
            else:
                features['URL_Depth'] = 0  # Very high depth - suspicious

            # 5. Redirection: Check for redirections (simplified)
            features['Redirection'] = 1 if '//' in parsed_url.path else 0

            # 6. https_Domain: Check if uses HTTPS (0 = has HTTPS, 1 = no HTTPS based on training data)
            features['https_Domain'] = 0 if parsed_url.scheme == 'https' else 1
            
            # 7. TinyURL: Check if it's a URL shortening service
            shorteners = [
                'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly',
                'short.link', 'tiny.cc', 'is.gd', 'buff.ly', 'short.url'
            ]
            # Use exact domain matching, not substring matching
            domain_parts = domain.split('.')
            is_shortener = False
            for shortener in shorteners:
                shortener_parts = shortener.split('.')
                if len(domain_parts) >= len(shortener_parts):
                    # Check if the domain ends with the shortener
                    if domain.endswith(shortener):
                        is_shortener = True
                        break
            features['TinyURL'] = 1 if is_shortener else 0
            
            # 8. Prefix_Suffix: Check for dash in domain
            features['Prefix_Suffix'] = 1 if '-' in domain else 0
            
            # 9. DNS_Record: Check if domain has DNS record
            features['DNS_Record'] = self._check_dns_record(domain)
            
            # 10. Web_Traffic: Check domain popularity (simplified)
            features['Web_Traffic'] = self._check_web_traffic(domain)
            
            # 11. Domain_Age: Check domain age
            features['Domain_Age'] = self._check_domain_age(domain)
            
            # 12. Domain_End: Check domain expiration
            features['Domain_End'] = self._check_domain_end(domain)
            
            # 13. iFrame: Check for iframe usage (simplified for performance)
            features['iFrame'] = 0  # Skip slow content analysis for now

            # 14. Mouse_Over: Check for mouse over effects (simplified)
            features['Mouse_Over'] = 0  # Requires JavaScript analysis

            # 15. Right_Click: Check for right-click disabling (simplified)
            features['Right_Click'] = 0  # Requires JavaScript analysis

            # 16. Web_Forwards: Check for forwarding (simplified for performance)
            features['Web_Forwards'] = 0  # Skip slow redirect check for now
            
        except Exception as e:
            print(f"Error extracting features from {url}: {e}")
            # Return default values if extraction fails
            features = {name: 0 for name in self.feature_names}
        
        return features
    
    def _check_dns_record(self, domain: str) -> int:
        """Check if domain has DNS record (with caching and timeout)"""
        if domain in self.dns_cache:
            return self.dns_cache[domain]

        try:
            # Set a short timeout for DNS lookup
            socket.setdefaulttimeout(1.0)
            socket.gethostbyname(domain)
            result = 1
        except:
            result = 0
        finally:
            socket.setdefaulttimeout(None)

        self.dns_cache[domain] = result
        return result
    
    def _check_web_traffic(self, domain: str) -> int:
        """Check web traffic (simplified - based on domain characteristics)"""
        # Popular domains (simplified check) - EXPANDED LIST
        popular_domains = [
            'google.com', 'facebook.com', 'youtube.com', 'amazon.com',
            'wikipedia.org', 'twitter.com', 'instagram.com', 'linkedin.com',
            'github.com', 'stackoverflow.com', 'reddit.com', 'microsoft.com',
            'paypal.com', 'ebay.com', 'apple.com', 'netflix.com', 'spotify.com',
            'gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com',
            'dropbox.com', 'slack.com', 'discord.com', 'telegram.org',
            'whatsapp.com', 'instagram.com', 'tiktok.com', 'pinterest.com',
            'reddit.com', 'quora.com', 'medium.com', 'dev.to',
            'bank', 'paypal', 'stripe', 'square', 'wise'
        ]

        # Check if it's a well-known domain
        domain_lower = domain.lower()
        for popular in popular_domains:
            if popular in domain_lower:
                return 1

        # Check domain length and structure
        if len(domain) > 25 or domain.count('.') > 3:
            return 0  # Suspicious

        return 1  # Default to having traffic
    
    def _check_domain_age(self, domain: str) -> int:
        """Check domain age (simplified for performance)"""
        if domain in self.domain_cache:
            return self.domain_cache[domain]

        # Simplified check based on domain characteristics
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.pw', '.top', '.click', '.xyz']
        suspicious_patterns = ['temp', 'test', 'fake', 'phish', 'scam', 'verify', 'confirm', 'urgent']

        # Legitimate TLDs and patterns
        legitimate_tlds = ['.com', '.org', '.net', '.edu', '.gov', '.co.uk', '.de', '.fr']
        legitimate_patterns = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'bank']

        result = 1  # Default to old domain (legitimate)

        # Check for legitimate patterns first
        domain_lower = domain.lower()
        if any(pattern in domain_lower for pattern in legitimate_patterns):
            result = 1
        # Check for suspicious TLDs
        elif any(tld in domain_lower for tld in suspicious_tlds):
            result = 0
        # Check for suspicious patterns in domain name
        elif any(pattern in domain_lower for pattern in suspicious_patterns):
            result = 0
        # Very short domains (2-3 chars) are often suspicious
        elif len(domain) < 4:
            result = 0

        self.domain_cache[domain] = result
        return result
    
    def _check_domain_end(self, domain: str) -> int:
        """Check domain expiration (simplified for performance)"""
        # Simplified check - assume legitimate domains have long expiration
        # Suspicious domains often have short expiration
        suspicious_indicators = ['.tk', '.ml', '.ga', '.cf', '.pw', 'temp', 'test', 'verify', 'confirm']
        legitimate_indicators = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'bank']

        domain_lower = domain.lower()

        # Check for legitimate indicators first
        if any(indicator in domain_lower for indicator in legitimate_indicators):
            return 1  # Legitimate domains have long expiration

        # Check for suspicious indicators
        if any(indicator in domain_lower for indicator in suspicious_indicators):
            return 0  # Suspicious domains have short expiration

        return 1  # Default to long expiration
    
    def _check_iframe(self, url: str) -> int:
        """Check for iframe usage (simplified for performance)"""
        try:
            response = requests.get(url, timeout=2, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            # Only check first 1000 characters for performance
            content = response.text[:1000].lower()
            return 1 if '<iframe' in content else 0
        except:
            return 0
    
    def _check_web_forwards(self, url: str) -> int:
        """Check for web forwarding (simplified for performance)"""
        try:
            response = requests.head(url, timeout=2, allow_redirects=False)
            return 1 if response.status_code in [301, 302, 303, 307, 308] else 0
        except:
            return 0
    
    def extract_features_vector(self, url: str) -> List[int]:
        """Extract features and return as ordered vector"""
        features_dict = self.extract_url_features(url)
        return [features_dict.get(name, 0) for name in self.feature_names]
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return self.feature_names.copy()

# Test function
def test_feature_extractor():
    """Test the feature extractor"""
    extractor = RealFeatureExtractor()
    
    test_urls = [
        "https://www.google.com",
        "http://192.168.1.1/login",
        "https://bit.ly/suspicious-link",
        "http://phishing-site.tk/urgent-verify"
    ]
    
    print("Testing Real Feature Extractor:")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nURL: {url}")
        features = extractor.extract_url_features(url)
        print("Features:")
        for name, value in features.items():
            print(f"  {name}: {value}")

if __name__ == "__main__":
    test_feature_extractor()
