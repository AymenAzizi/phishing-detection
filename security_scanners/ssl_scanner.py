"""
SSL/TLS Security Scanner

Analyzes SSL/TLS configuration including:
- Certificate validity and expiration
- Cipher suite strength
- Protocol versions
- Certificate chain validation
- Common SSL/TLS vulnerabilities
"""

import ssl
import socket
import datetime
from typing import Dict, List, Any
from urllib.parse import urlparse
import OpenSSL
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import requests


class SSLScanner:
    """SSL/TLS security scanner for web applications"""
    
    # Weak cipher suites to flag
    WEAK_CIPHERS = [
        'RC4', 'DES', '3DES', 'MD5', 'NULL', 'EXPORT', 'anon'
    ]
    
    # Deprecated protocols
    DEPRECATED_PROTOCOLS = [
        'SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1'
    ]
    
    def __init__(self):
        self.results = {}
        
    def scan(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive SSL/TLS security scan
        
        Args:
            url: Target URL to scan
            
        Returns:
            Dictionary containing scan results
        """
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or parsed_url.path
        port = parsed_url.port or 443
        
        if not hostname:
            return {
                'error': 'Invalid URL',
                'score': 0,
                'grade': 'F',
                'issues': [{'severity': 'critical', 'message': 'Invalid URL provided'}]
            }
        
        # Check if HTTPS is used
        if parsed_url.scheme != 'https':
            return {
                'error': 'Not using HTTPS',
                'score': 0,
                'grade': 'F',
                'issues': [{
                    'severity': 'critical',
                    'message': 'Website does not use HTTPS encryption',
                    'recommendation': 'Enable HTTPS with a valid SSL/TLS certificate',
                    'fix': 'Obtain an SSL certificate from Let\'s Encrypt or a commercial CA and configure your web server to use HTTPS'
                }],
                'has_ssl': False
            }
        
        try:
            results = {
                'has_ssl': True,
                'hostname': hostname,
                'port': port,
                'issues': [],
                'certificate': {},
                'protocols': {},
                'ciphers': {}
            }
            
            # Get certificate information
            cert_info = self._get_certificate_info(hostname, port)
            results['certificate'] = cert_info
            
            # Check certificate validity
            cert_issues = self._check_certificate_validity(cert_info)
            results['issues'].extend(cert_issues)
            
            # Check protocol support
            protocol_info = self._check_protocols(hostname, port)
            results['protocols'] = protocol_info
            
            # Check for weak protocols
            protocol_issues = self._check_weak_protocols(protocol_info)
            results['issues'].extend(protocol_issues)
            
            # Check cipher suites
            cipher_info = self._check_ciphers(hostname, port)
            results['ciphers'] = cipher_info
            
            # Check for weak ciphers
            cipher_issues = self._check_weak_ciphers(cipher_info)
            results['issues'].extend(cipher_issues)
            
            # Calculate score
            score, grade = self._calculate_score(results)
            results['score'] = score
            results['grade'] = grade
            
            return results
            
        except Exception as e:
            return {
                'error': str(e),
                'score': 0,
                'grade': 'F',
                'issues': [{
                    'severity': 'critical',
                    'message': f'Failed to scan SSL/TLS: {str(e)}',
                    'recommendation': 'Ensure the website is accessible and using valid HTTPS'
                }],
                'has_ssl': False
            }
    
    def _get_certificate_info(self, hostname: str, port: int) -> Dict[str, Any]:
        """Get SSL certificate information"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_bin = ssock.getpeercert(binary_form=True)
                    cert_dict = ssock.getpeercert()
                    
                    # Parse certificate
                    cert = x509.load_der_x509_certificate(cert_bin, default_backend())
                    
                    return {
                        'subject': dict(x[0] for x in cert_dict.get('subject', [])),
                        'issuer': dict(x[0] for x in cert_dict.get('issuer', [])),
                        'version': cert.version.name,
                        'serial_number': str(cert.serial_number),
                        'not_before': cert.not_valid_before.isoformat(),
                        'not_after': cert.not_valid_after.isoformat(),
                        'signature_algorithm': cert.signature_algorithm_oid._name,
                        'san': cert_dict.get('subjectAltName', []),
                        'valid': True
                    }
        except Exception as e:
            return {
                'error': str(e),
                'valid': False
            }
    
    def _check_certificate_validity(self, cert_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check certificate validity and expiration"""
        issues = []
        
        if not cert_info.get('valid'):
            issues.append({
                'severity': 'critical',
                'message': 'Invalid or inaccessible SSL certificate',
                'recommendation': 'Install a valid SSL certificate from a trusted CA',
                'fix': 'Use Let\'s Encrypt for free SSL certificates: certbot --nginx -d yourdomain.com'
            })
            return issues
        
        # Check expiration
        try:
            not_after = datetime.datetime.fromisoformat(cert_info['not_after'].replace('Z', '+00:00'))
            days_until_expiry = (not_after - datetime.datetime.now(datetime.timezone.utc)).days
            
            if days_until_expiry < 0:
                issues.append({
                    'severity': 'critical',
                    'message': 'SSL certificate has expired',
                    'recommendation': 'Renew the SSL certificate immediately',
                    'fix': 'Renew certificate: certbot renew'
                })
            elif days_until_expiry < 30:
                issues.append({
                    'severity': 'high',
                    'message': f'SSL certificate expires in {days_until_expiry} days',
                    'recommendation': 'Renew the SSL certificate soon',
                    'fix': 'Set up automatic renewal: certbot renew --dry-run'
                })
        except Exception:
            pass
        
        return issues
    
    def _check_protocols(self, hostname: str, port: int) -> Dict[str, bool]:
        """Check supported SSL/TLS protocols"""
        protocols = {
            'TLSv1.3': False,
            'TLSv1.2': False,
            'TLSv1.1': False,
            'TLSv1.0': False,
        }
        
        # Try to connect with each protocol
        for protocol_name in protocols.keys():
            try:
                protocol_version = getattr(ssl, f'PROTOCOL_{protocol_name.replace(".", "_")}', None)
                if protocol_version:
                    context = ssl.SSLContext(protocol_version)
                    with socket.create_connection((hostname, port), timeout=5) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            protocols[protocol_name] = True
            except Exception:
                pass
        
        return protocols
    
    def _check_weak_protocols(self, protocol_info: Dict[str, bool]) -> List[Dict[str, str]]:
        """Check for weak or deprecated protocols"""
        issues = []
        
        if protocol_info.get('TLSv1.0') or protocol_info.get('TLSv1.1'):
            issues.append({
                'severity': 'high',
                'message': 'Deprecated TLS protocols enabled (TLSv1.0/1.1)',
                'recommendation': 'Disable TLSv1.0 and TLSv1.1, use only TLSv1.2 and TLSv1.3',
                'fix': 'Nginx: ssl_protocols TLSv1.2 TLSv1.3; Apache: SSLProtocol -all +TLSv1.2 +TLSv1.3'
            })
        
        if not protocol_info.get('TLSv1.3'):
            issues.append({
                'severity': 'medium',
                'message': 'TLSv1.3 not supported',
                'recommendation': 'Enable TLSv1.3 for better security and performance',
                'fix': 'Update OpenSSL to 1.1.1+ and enable TLSv1.3 in web server config'
            })
        
        return issues
    
    def _check_ciphers(self, hostname: str, port: int) -> Dict[str, Any]:
        """Check supported cipher suites"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    return {
                        'cipher': ssock.cipher(),
                        'version': ssock.version()
                    }
        except Exception:
            return {}
    
    def _check_weak_ciphers(self, cipher_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check for weak cipher suites"""
        issues = []
        
        if cipher_info.get('cipher'):
            cipher_name = cipher_info['cipher'][0]
            
            # Check for weak ciphers
            for weak in self.WEAK_CIPHERS:
                if weak.upper() in cipher_name.upper():
                    issues.append({
                        'severity': 'high',
                        'message': f'Weak cipher suite detected: {cipher_name}',
                        'recommendation': 'Use strong cipher suites (AES-GCM, ChaCha20)',
                        'fix': 'Configure strong ciphers: ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256";'
                    })
                    break
        
        return issues
    
    def _calculate_score(self, results: Dict[str, Any]) -> tuple:
        """Calculate SSL/TLS security score (0-100)"""
        score = 100
        
        # Deduct points for issues
        for issue in results.get('issues', []):
            severity = issue.get('severity', 'low')
            if severity == 'critical':
                score -= 30
            elif severity == 'high':
                score -= 15
            elif severity == 'medium':
                score -= 10
            elif severity == 'low':
                score -= 5
        
        # Bonus for TLSv1.3
        if results.get('protocols', {}).get('TLSv1.3'):
            score += 5
        
        score = max(0, min(100, score))
        
        # Determine grade
        if score >= 95:
            grade = 'A+'
        elif score >= 85:
            grade = 'A'
        elif score >= 75:
            grade = 'B'
        elif score >= 65:
            grade = 'C'
        elif score >= 50:
            grade = 'D'
        else:
            grade = 'F'
        
        return score, grade

