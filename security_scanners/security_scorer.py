"""
Security Scorer

Aggregates results from all security scanners and calculates:
- Overall security score (0-100)
- Security grade (A+ to F)
- Comprehensive security report
- Prioritized recommendations
"""

from typing import Dict, List, Any
from datetime import datetime


class SecurityScorer:
    """Unified security scoring system"""
    
    # Weight for each scanner type
    SCANNER_WEIGHTS = {
        'ssl': 0.25,        # 25% - SSL/TLS is critical
        'headers': 0.20,    # 20% - Security headers important
        'vulnerabilities': 0.30,  # 30% - Vulnerabilities most critical
        'phishing': 0.25    # 25% - Phishing detection important
    }
    
    def __init__(self):
        pass
    
    def calculate_overall_score(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall security score from all scanner results
        
        Args:
            scan_results: Dictionary containing results from all scanners
            
        Returns:
            Dictionary with overall score, grade, and aggregated results
        """
        scores = {}
        total_weight = 0
        weighted_score = 0
        
        # Extract scores from each scanner
        for scanner_type, weight in self.SCANNER_WEIGHTS.items():
            if scanner_type in scan_results and 'score' in scan_results[scanner_type]:
                score = scan_results[scanner_type]['score']
                scores[scanner_type] = score
                weighted_score += score * weight
                total_weight += weight
        
        # Calculate overall score
        if total_weight > 0:
            overall_score = round(weighted_score / total_weight, 1)
        else:
            overall_score = 0
        
        # Determine grade
        grade = self._get_grade(overall_score)
        
        # Aggregate all issues
        all_issues = self._aggregate_issues(scan_results)
        
        # Prioritize recommendations
        recommendations = self._prioritize_recommendations(all_issues)
        
        # Generate summary
        summary = self._generate_summary(scan_results, overall_score, grade)
        
        return {
            'overall_score': overall_score,
            'grade': grade,
            'scanner_scores': scores,
            'total_issues': len(all_issues),
            'issues_by_severity': self._count_by_severity(all_issues),
            'all_issues': all_issues,
            'top_recommendations': recommendations[:10],  # Top 10
            'summary': summary,
            'scan_timestamp': datetime.utcnow().isoformat(),
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'A-'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        elif score >= 55:
            return 'C-'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def _aggregate_issues(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate all issues from all scanners"""
        all_issues = []
        
        for scanner_type, results in scan_results.items():
            if isinstance(results, dict) and 'issues' in results:
                for issue in results['issues']:
                    issue_copy = issue.copy()
                    issue_copy['scanner'] = scanner_type
                    all_issues.append(issue_copy)
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_issues.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 4))
        
        return all_issues
    
    def _count_by_severity(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count issues by severity level"""
        counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def _prioritize_recommendations(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize recommendations based on severity and impact"""
        recommendations = []
        
        for issue in issues:
            if 'recommendation' in issue:
                rec = {
                    'severity': issue.get('severity', 'low'),
                    'scanner': issue.get('scanner', 'unknown'),
                    'message': issue.get('message', ''),
                    'recommendation': issue.get('recommendation', ''),
                    'fix': issue.get('fix', ''),
                    'priority': self._calculate_priority(issue)
                }
                recommendations.append(rec)
        
        # Sort by priority (higher first)
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        return recommendations
    
    def _calculate_priority(self, issue: Dict[str, Any]) -> int:
        """Calculate priority score for an issue"""
        severity_scores = {
            'critical': 100,
            'high': 75,
            'medium': 50,
            'low': 25
        }
        
        base_score = severity_scores.get(issue.get('severity', 'low'), 0)
        
        # Boost priority for certain types
        if issue.get('type') == 'sqli':
            base_score += 20
        elif issue.get('type') == 'xss':
            base_score += 15
        elif issue.get('scanner') == 'ssl':
            base_score += 10
        
        return base_score
    
    def _generate_summary(self, scan_results: Dict[str, Any], overall_score: float, grade: str) -> Dict[str, Any]:
        """Generate human-readable summary"""
        
        # Determine security level
        if overall_score >= 90:
            security_level = 'Excellent'
            description = 'Your website has excellent security practices in place.'
        elif overall_score >= 75:
            security_level = 'Good'
            description = 'Your website has good security, but there are some improvements needed.'
        elif overall_score >= 60:
            security_level = 'Fair'
            description = 'Your website has fair security, but several issues need attention.'
        elif overall_score >= 40:
            security_level = 'Poor'
            description = 'Your website has poor security with multiple critical issues.'
        else:
            security_level = 'Critical'
            description = 'Your website has critical security issues that need immediate attention.'
        
        # Count scanners run
        scanners_run = []
        for scanner_type in ['ssl', 'headers', 'vulnerabilities', 'phishing']:
            if scanner_type in scan_results:
                scanners_run.append(scanner_type)
        
        return {
            'security_level': security_level,
            'description': description,
            'scanners_run': scanners_run,
            'scan_complete': len(scanners_run) == 4
        }
    
    def generate_report_data(self, url: str, scan_results: Dict[str, Any], overall_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report data for PDF/JSON export"""
        
        return {
            'report_metadata': {
                'url': url,
                'scan_date': datetime.utcnow().isoformat(),
                'scanner_version': '1.0.0',
                'report_type': 'Comprehensive Security Scan'
            },
            'executive_summary': {
                'overall_score': overall_results['overall_score'],
                'grade': overall_results['grade'],
                'security_level': overall_results['summary']['security_level'],
                'description': overall_results['summary']['description'],
                'total_issues': overall_results['total_issues'],
                'critical_issues': overall_results['issues_by_severity']['critical'],
                'high_issues': overall_results['issues_by_severity']['high']
            },
            'scanner_results': {
                'ssl_tls': scan_results.get('ssl', {}),
                'security_headers': scan_results.get('headers', {}),
                'vulnerabilities': scan_results.get('vulnerabilities', {}),
                'phishing_detection': scan_results.get('phishing', {})
            },
            'detailed_findings': overall_results['all_issues'],
            'recommendations': overall_results['top_recommendations'],
            'next_steps': self._generate_next_steps(overall_results)
        }
    
    def _generate_next_steps(self, overall_results: Dict[str, Any]) -> List[str]:
        """Generate actionable next steps"""
        next_steps = []
        
        severity_counts = overall_results['issues_by_severity']
        
        if severity_counts['critical'] > 0:
            next_steps.append(f"🚨 Address {severity_counts['critical']} critical security issues immediately")
        
        if severity_counts['high'] > 0:
            next_steps.append(f"⚠️ Fix {severity_counts['high']} high-severity issues within 7 days")
        
        if severity_counts['medium'] > 0:
            next_steps.append(f"📋 Plan to resolve {severity_counts['medium']} medium-severity issues within 30 days")
        
        # Add specific recommendations
        if overall_results['overall_score'] < 60:
            next_steps.append("📚 Review OWASP Top 10 security risks")
            next_steps.append("🔒 Implement a Web Application Firewall (WAF)")
        
        if overall_results['overall_score'] < 80:
            next_steps.append("🛡️ Enable all recommended security headers")
            next_steps.append("🔐 Ensure all connections use HTTPS with strong TLS")
        
        next_steps.append("🔄 Schedule regular security scans (weekly recommended)")
        next_steps.append("📊 Monitor security improvements over time")
        
        return next_steps

