"""
Security Headers Scanner

Analyzes HTTP security headers including:
- Content-Security-Policy (CSP)
- Strict-Transport-Security (HSTS)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy
"""

import requests
from typing import Dict, List, Any
from urllib.parse import urlparse


class SecurityHeadersScanner:
    """HTTP security headers scanner"""
    
    # Required security headers
    REQUIRED_HEADERS = {
        'Strict-Transport-Security': {
            'severity': 'high',
            'description': 'HSTS header missing - site vulnerable to SSL stripping attacks',
            'recommendation': 'Add HSTS header to enforce HTTPS',
            'fix': 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload'
        },
        'X-Frame-Options': {
            'severity': 'high',
            'description': 'X-Frame-Options missing - site vulnerable to clickjacking',
            'recommendation': 'Add X-Frame-Options header to prevent clickjacking',
            'fix': 'X-Frame-Options: DENY or SAMEORIGIN'
        },
        'X-Content-Type-Options': {
            'severity': 'medium',
            'description': 'X-Content-Type-Options missing - MIME type sniffing possible',
            'recommendation': 'Add X-Content-Type-Options header',
            'fix': 'X-Content-Type-Options: nosniff'
        },
        'Content-Security-Policy': {
            'severity': 'high',
            'description': 'CSP header missing - vulnerable to XSS and injection attacks',
            'recommendation': 'Implement Content Security Policy',
            'fix': "Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none';"
        },
        'Referrer-Policy': {
            'severity': 'low',
            'description': 'Referrer-Policy missing - may leak sensitive URLs',
            'recommendation': 'Add Referrer-Policy header',
            'fix': 'Referrer-Policy: strict-origin-when-cross-origin'
        },
        'Permissions-Policy': {
            'severity': 'low',
            'description': 'Permissions-Policy missing - browser features not restricted',
            'recommendation': 'Add Permissions-Policy header',
            'fix': 'Permissions-Policy: geolocation=(), microphone=(), camera=()'
        }
    }
    
    # Insecure header values
    INSECURE_VALUES = {
        'X-Frame-Options': ['ALLOW-FROM'],
        'X-XSS-Protection': ['0'],
    }
    
    def __init__(self):
        self.results = {}
    
    def scan(self, url: str) -> Dict[str, Any]:
        """
        Scan HTTP security headers
        
        Args:
            url: Target URL to scan
            
        Returns:
            Dictionary containing scan results
        """
        try:
            # Make request with timeout
            response = requests.get(
                url,
                timeout=10,
                allow_redirects=True,
                verify=True,
                headers={'User-Agent': 'DevSecScan/1.0 Security Scanner'}
            )
            
            headers = response.headers
            
            results = {
                'url': url,
                'status_code': response.status_code,
                'headers_found': {},
                'headers_missing': [],
                'issues': [],
                'recommendations': []
            }
            
            # Check each required header
            for header_name, header_info in self.REQUIRED_HEADERS.items():
                if header_name in headers:
                    results['headers_found'][header_name] = headers[header_name]
                    
                    # Check for insecure values
                    insecure_check = self._check_insecure_value(
                        header_name, 
                        headers[header_name]
                    )
                    if insecure_check:
                        results['issues'].append(insecure_check)
                    
                    # Validate header value
                    validation = self._validate_header(header_name, headers[header_name])
                    if validation:
                        results['issues'].extend(validation)
                else:
                    results['headers_missing'].append(header_name)
                    results['issues'].append({
                        'severity': header_info['severity'],
                        'header': header_name,
                        'message': header_info['description'],
                        'recommendation': header_info['recommendation'],
                        'fix': header_info['fix']
                    })
            
            # Check for deprecated headers
            deprecated = self._check_deprecated_headers(headers)
            results['issues'].extend(deprecated)
            
            # Check for information disclosure
            disclosure = self._check_information_disclosure(headers)
            results['issues'].extend(disclosure)
            
            # Calculate score
            score, grade = self._calculate_score(results)
            results['score'] = score
            results['grade'] = grade
            
            return results
            
        except requests.exceptions.SSLError as e:
            return {
                'error': 'SSL Error',
                'message': str(e),
                'score': 0,
                'grade': 'F',
                'issues': [{
                    'severity': 'critical',
                    'message': 'SSL certificate validation failed',
                    'recommendation': 'Fix SSL certificate issues first',
                    'fix': 'Ensure valid SSL certificate is installed'
                }]
            }
        except requests.exceptions.Timeout:
            return {
                'error': 'Timeout',
                'message': 'Request timed out',
                'score': 0,
                'grade': 'F',
                'issues': [{
                    'severity': 'critical',
                    'message': 'Website did not respond within timeout period',
                    'recommendation': 'Check if website is accessible'
                }]
            }
        except Exception as e:
            return {
                'error': str(e),
                'score': 0,
                'grade': 'F',
                'issues': [{
                    'severity': 'critical',
                    'message': f'Failed to scan headers: {str(e)}',
                    'recommendation': 'Ensure the website is accessible'
                }]
            }
    
    def _check_insecure_value(self, header_name: str, value: str) -> Dict[str, str]:
        """Check if header has insecure value"""
        if header_name in self.INSECURE_VALUES:
            for insecure_val in self.INSECURE_VALUES[header_name]:
                if insecure_val.lower() in value.lower():
                    return {
                        'severity': 'high',
                        'header': header_name,
                        'message': f'{header_name} has insecure value: {value}',
                        'recommendation': f'Change {header_name} to a secure value',
                        'fix': self.REQUIRED_HEADERS[header_name]['fix']
                    }
        return None
    
    def _validate_header(self, header_name: str, value: str) -> List[Dict[str, str]]:
        """Validate specific header values"""
        issues = []
        
        if header_name == 'Strict-Transport-Security':
            # Check max-age
            if 'max-age' not in value.lower():
                issues.append({
                    'severity': 'high',
                    'header': header_name,
                    'message': 'HSTS header missing max-age directive',
                    'recommendation': 'Add max-age directive to HSTS header',
                    'fix': 'Strict-Transport-Security: max-age=31536000; includeSubDomains'
                })
            else:
                # Extract max-age value
                try:
                    max_age = int(value.split('max-age=')[1].split(';')[0].strip())
                    if max_age < 31536000:  # Less than 1 year
                        issues.append({
                            'severity': 'medium',
                            'header': header_name,
                            'message': f'HSTS max-age is too short: {max_age} seconds',
                            'recommendation': 'Set HSTS max-age to at least 1 year (31536000 seconds)',
                            'fix': 'Strict-Transport-Security: max-age=31536000; includeSubDomains'
                        })
                except Exception:
                    pass
            
            # Check includeSubDomains
            if 'includesubdomains' not in value.lower():
                issues.append({
                    'severity': 'low',
                    'header': header_name,
                    'message': 'HSTS header missing includeSubDomains directive',
                    'recommendation': 'Add includeSubDomains to protect all subdomains',
                    'fix': 'Strict-Transport-Security: max-age=31536000; includeSubDomains'
                })
        
        elif header_name == 'Content-Security-Policy':
            # Check for unsafe-inline
            if "'unsafe-inline'" in value:
                issues.append({
                    'severity': 'medium',
                    'header': header_name,
                    'message': "CSP contains 'unsafe-inline' which weakens XSS protection",
                    'recommendation': "Remove 'unsafe-inline' and use nonces or hashes",
                    'fix': "Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}';"
                })
            
            # Check for unsafe-eval
            if "'unsafe-eval'" in value:
                issues.append({
                    'severity': 'medium',
                    'header': header_name,
                    'message': "CSP contains 'unsafe-eval' which allows dangerous eval()",
                    'recommendation': "Remove 'unsafe-eval' from CSP",
                    'fix': "Content-Security-Policy: default-src 'self'; script-src 'self';"
                })
        
        return issues
    
    def _check_deprecated_headers(self, headers: Dict[str, str]) -> List[Dict[str, str]]:
        """Check for deprecated security headers"""
        issues = []
        
        # X-XSS-Protection is deprecated
        if 'X-XSS-Protection' in headers:
            issues.append({
                'severity': 'low',
                'header': 'X-XSS-Protection',
                'message': 'X-XSS-Protection header is deprecated',
                'recommendation': 'Remove X-XSS-Protection and use Content-Security-Policy instead',
                'fix': "Content-Security-Policy: default-src 'self';"
            })
        
        return issues
    
    def _check_information_disclosure(self, headers: Dict[str, str]) -> List[Dict[str, str]]:
        """Check for headers that disclose sensitive information"""
        issues = []
        
        disclosure_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version', 'X-AspNetMvc-Version']
        
        for header in disclosure_headers:
            if header in headers:
                issues.append({
                    'severity': 'low',
                    'header': header,
                    'message': f'{header} header discloses server information: {headers[header]}',
                    'recommendation': f'Remove or obfuscate {header} header',
                    'fix': f'Configure web server to remove {header} header'
                })
        
        return issues
    
    def _calculate_score(self, results: Dict[str, Any]) -> tuple:
        """Calculate security headers score (0-100)"""
        score = 100
        
        # Deduct points for issues
        for issue in results.get('issues', []):
            severity = issue.get('severity', 'low')
            if severity == 'critical':
                score -= 25
            elif severity == 'high':
                score -= 15
            elif severity == 'medium':
                score -= 10
            elif severity == 'low':
                score -= 5
        
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

