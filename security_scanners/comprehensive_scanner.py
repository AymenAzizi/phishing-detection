"""
Comprehensive Security Scanner

Orchestrates all security scanners and provides unified results:
- SSL/TLS security
- Security headers
- Vulnerability detection
- Phishing detection (ML-based)
- Unified scoring and reporting
"""

import asyncio
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import logging

from .ssl_scanner import SSLScanner
from .headers_scanner import SecurityHeadersScanner
from .vulnerability_scanner import VulnerabilityScanner
from .security_scorer import SecurityScorer

# Import phishing detector from existing module
try:
    from real_feature_extraction import extract_features
    from real_model_trainer import load_model
    PHISHING_AVAILABLE = True
except ImportError:
    PHISHING_AVAILABLE = False
    logging.warning("Phishing detection module not available")


class ComprehensiveScanner:
    """Orchestrates all security scanners for comprehensive analysis"""
    
    def __init__(self):
        self.ssl_scanner = SSLScanner()
        self.headers_scanner = SecurityHeadersScanner()
        self.vulnerability_scanner = VulnerabilityScanner()
        self.security_scorer = SecurityScorer()
        
        # Load phishing model if available
        self.phishing_model = None
        if PHISHING_AVAILABLE:
            try:
                self.phishing_model = load_model()
            except Exception as e:
                logging.warning(f"Failed to load phishing model: {e}")
    
    def scan(
        self,
        url: str,
        scan_types: Optional[List[str]] = None,
        depth: str = 'standard'
    ) -> Dict[str, Any]:
        """
        Perform comprehensive security scan
        
        Args:
            url: Target URL to scan
            scan_types: List of scan types to run (default: all)
                       Options: ['ssl', 'headers', 'vulnerabilities', 'phishing']
            depth: Scan depth - 'quick', 'standard', or 'deep'
            
        Returns:
            Dictionary containing all scan results and overall score
        """
        # Default to all scan types
        if scan_types is None:
            scan_types = ['ssl', 'headers', 'vulnerabilities', 'phishing']
        
        results = {
            'url': url,
            'scan_depth': depth,
            'scan_types': scan_types,
            'scans': {}
        }
        
        # Run scanners in parallel for better performance
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            if 'ssl' in scan_types:
                futures['ssl'] = executor.submit(self._run_ssl_scan, url)
            
            if 'headers' in scan_types:
                futures['headers'] = executor.submit(self._run_headers_scan, url)
            
            if 'vulnerabilities' in scan_types:
                futures['vulnerabilities'] = executor.submit(
                    self._run_vulnerability_scan, url, depth
                )
            
            if 'phishing' in scan_types:
                futures['phishing'] = executor.submit(self._run_phishing_scan, url)
            
            # Collect results
            for scan_type, future in futures.items():
                try:
                    results['scans'][scan_type] = future.result(timeout=30)
                except Exception as e:
                    results['scans'][scan_type] = {
                        'error': str(e),
                        'score': 0,
                        'grade': 'F'
                    }
        
        # Calculate overall score
        overall_results = self.security_scorer.calculate_overall_score(results['scans'])
        results['overall'] = overall_results
        
        # Generate report data
        results['report'] = self.security_scorer.generate_report_data(
            url,
            results['scans'],
            overall_results
        )
        
        return results
    
    def _run_ssl_scan(self, url: str) -> Dict[str, Any]:
        """Run SSL/TLS security scan"""
        try:
            return self.ssl_scanner.scan(url)
        except Exception as e:
            logging.error(f"SSL scan failed: {e}")
            return {
                'error': str(e),
                'score': 0,
                'grade': 'F',
                'issues': [{
                    'severity': 'critical',
                    'message': f'SSL scan failed: {str(e)}'
                }]
            }
    
    def _run_headers_scan(self, url: str) -> Dict[str, Any]:
        """Run security headers scan"""
        try:
            return self.headers_scanner.scan(url)
        except Exception as e:
            logging.error(f"Headers scan failed: {e}")
            return {
                'error': str(e),
                'score': 0,
                'grade': 'F',
                'issues': [{
                    'severity': 'critical',
                    'message': f'Headers scan failed: {str(e)}'
                }]
            }
    
    def _run_vulnerability_scan(self, url: str, depth: str) -> Dict[str, Any]:
        """Run vulnerability scan"""
        try:
            return self.vulnerability_scanner.scan(url)
        except Exception as e:
            logging.error(f"Vulnerability scan failed: {e}")
            return {
                'error': str(e),
                'score': 0,
                'grade': 'F',
                'issues': [{
                    'severity': 'critical',
                    'message': f'Vulnerability scan failed: {str(e)}'
                }]
            }
    
    def _run_phishing_scan(self, url: str) -> Dict[str, Any]:
        """Run phishing detection scan using ML model"""
        try:
            if not PHISHING_AVAILABLE or self.phishing_model is None:
                return {
                    'error': 'Phishing detection not available',
                    'score': 50,
                    'grade': 'C',
                    'issues': []
                }
            
            # Extract features
            features = extract_features(url)
            
            # Make prediction
            prediction = self.phishing_model.predict([features])[0]
            probability = self.phishing_model.predict_proba([features])[0]
            
            is_phishing = prediction == 1
            confidence = probability[1] if is_phishing else probability[0]
            
            issues = []
            if is_phishing:
                issues.append({
                    'severity': 'critical',
                    'type': 'phishing',
                    'message': f'Phishing website detected (confidence: {confidence:.1%})',
                    'recommendation': 'Do not enter any personal information on this website',
                    'fix': 'This website appears to be a phishing attempt. Avoid visiting it.'
                })
            
            # Calculate score (inverse of phishing probability)
            score = int((1 - probability[1]) * 100)
            
            # Determine grade
            if score >= 90:
                grade = 'A+'
            elif score >= 80:
                grade = 'A'
            elif score >= 70:
                grade = 'B'
            elif score >= 60:
                grade = 'C'
            elif score >= 50:
                grade = 'D'
            else:
                grade = 'F'
            
            return {
                'is_phishing': is_phishing,
                'confidence': float(confidence),
                'phishing_probability': float(probability[1]),
                'legitimate_probability': float(probability[0]),
                'score': score,
                'grade': grade,
                'issues': issues,
                'features_analyzed': len(features)
            }
            
        except Exception as e:
            logging.error(f"Phishing scan failed: {e}")
            return {
                'error': str(e),
                'score': 50,
                'grade': 'C',
                'issues': [{
                    'severity': 'medium',
                    'message': f'Phishing scan failed: {str(e)}'
                }]
            }
    
    def quick_scan(self, url: str) -> Dict[str, Any]:
        """
        Quick scan - SSL and Headers only (fast)
        
        Args:
            url: Target URL
            
        Returns:
            Scan results
        """
        return self.scan(url, scan_types=['ssl', 'headers'], depth='quick')
    
    def standard_scan(self, url: str) -> Dict[str, Any]:
        """
        Standard scan - All scanners with standard depth
        
        Args:
            url: Target URL
            
        Returns:
            Scan results
        """
        return self.scan(url, scan_types=['ssl', 'headers', 'vulnerabilities', 'phishing'], depth='standard')
    
    def deep_scan(self, url: str) -> Dict[str, Any]:
        """
        Deep scan - All scanners with maximum depth (slower)
        
        Args:
            url: Target URL
            
        Returns:
            Scan results
        """
        return self.scan(url, scan_types=['ssl', 'headers', 'vulnerabilities', 'phishing'], depth='deep')
    
    def get_scan_summary(self, scan_results: Dict[str, Any]) -> str:
        """
        Generate human-readable summary of scan results
        
        Args:
            scan_results: Results from scan()
            
        Returns:
            Formatted summary string
        """
        overall = scan_results.get('overall', {})
        
        summary = f"""
DevSecScan Security Report
{'=' * 50}

URL: {scan_results.get('url', 'N/A')}
Overall Score: {overall.get('overall_score', 0)}/100 (Grade: {overall.get('grade', 'F')})
Security Level: {overall.get('summary', {}).get('security_level', 'Unknown')}

Issues Found:
  Critical: {overall.get('issues_by_severity', {}).get('critical', 0)}
  High:     {overall.get('issues_by_severity', {}).get('high', 0)}
  Medium:   {overall.get('issues_by_severity', {}).get('medium', 0)}
  Low:      {overall.get('issues_by_severity', {}).get('low', 0)}

Scanner Scores:
"""
        
        for scanner, score in overall.get('scanner_scores', {}).items():
            summary += f"  {scanner.upper()}: {score}/100\n"
        
        summary += f"\nTop Recommendations:\n"
        for i, rec in enumerate(overall.get('top_recommendations', [])[:5], 1):
            summary += f"  {i}. [{rec['severity'].upper()}] {rec['message']}\n"
        
        return summary

