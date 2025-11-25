#!/usr/bin/env python3
"""
Test script for security scanners
"""

from security_scanners import (
    SSLScanner,
    SecurityHeadersScanner,
    VulnerabilityScanner,
    ComprehensiveScanner
)

def test_ssl_scanner():
    """Test SSL/TLS scanner"""
    print("\n" + "="*60)
    print("🔐 Testing SSL/TLS Scanner")
    print("="*60)
    
    scanner = SSLScanner()
    
    # Test with a known good site
    print("\n📊 Scanning https://www.google.com...")
    results = scanner.scan("https://www.google.com")
    
    print(f"✅ Score: {results.get('score', 0)}/100")
    print(f"✅ Grade: {results.get('grade', 'N/A')}")
    print(f"✅ Issues found: {len(results.get('issues', []))}")
    
    if results.get('issues'):
        print("\n⚠️  Issues:")
        for issue in results['issues'][:3]:  # Show first 3
            print(f"  - [{issue['severity'].upper()}] {issue['message']}")

def test_headers_scanner():
    """Test security headers scanner"""
    print("\n" + "="*60)
    print("🛡️  Testing Security Headers Scanner")
    print("="*60)
    
    scanner = SecurityHeadersScanner()
    
    print("\n📊 Scanning https://www.google.com...")
    results = scanner.scan("https://www.google.com")
    
    print(f"✅ Score: {results.get('score', 0)}/100")
    print(f"✅ Grade: {results.get('grade', 'N/A')}")
    print(f"✅ Headers found: {len(results.get('headers_found', {}))}")
    print(f"✅ Headers missing: {len(results.get('headers_missing', []))}")
    
    if results.get('headers_missing'):
        print("\n⚠️  Missing headers:")
        for header in results['headers_missing'][:3]:
            print(f"  - {header}")

def test_vulnerability_scanner():
    """Test vulnerability scanner"""
    print("\n" + "="*60)
    print("⚠️  Testing Vulnerability Scanner")
    print("="*60)
    
    scanner = VulnerabilityScanner()
    
    print("\n📊 Scanning https://www.google.com...")
    results = scanner.scan("https://www.google.com")
    
    print(f"✅ Score: {results.get('score', 0)}/100")
    print(f"✅ Grade: {results.get('grade', 'N/A')}")
    print(f"✅ Issues found: {len(results.get('issues', []))}")
    
    if results.get('vulnerabilities'):
        print("\n📋 Vulnerability categories:")
        for vuln_type, vulns in results['vulnerabilities'].items():
            if vulns:
                print(f"  - {vuln_type}: {len(vulns)} issues")

def test_comprehensive_scanner():
    """Test comprehensive scanner"""
    print("\n" + "="*60)
    print("🚀 Testing Comprehensive Scanner")
    print("="*60)
    
    scanner = ComprehensiveScanner()
    
    print("\n📊 Running comprehensive scan on https://www.google.com...")
    print("⏳ This may take a few seconds...")
    
    results = scanner.scan("https://www.google.com")
    
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE SCAN RESULTS")
    print("="*60)
    
    overall = results.get('overall', {})
    print(f"\n🎯 Overall Score: {overall.get('overall_score', 0)}/100")
    print(f"🎯 Grade: {overall.get('grade', 'N/A')}")
    print(f"🎯 Security Level: {overall.get('summary', {}).get('security_level', 'Unknown')}")
    
    print(f"\n📊 Total Issues: {overall.get('total_issues', 0)}")
    severity_counts = overall.get('issues_by_severity', {})
    print(f"  - Critical: {severity_counts.get('critical', 0)}")
    print(f"  - High: {severity_counts.get('high', 0)}")
    print(f"  - Medium: {severity_counts.get('medium', 0)}")
    print(f"  - Low: {severity_counts.get('low', 0)}")
    
    print(f"\n🔍 Scanner Scores:")
    for scanner_name, score in overall.get('scanner_scores', {}).items():
        print(f"  - {scanner_name.upper()}: {score}/100")
    
    print(f"\n💡 Top Recommendations:")
    for i, rec in enumerate(overall.get('top_recommendations', [])[:5], 1):
        print(f"  {i}. [{rec['severity'].upper()}] {rec['message']}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔒 DevSecScan Security Scanner Test Suite")
    print("="*60)
    
    try:
        # Test individual scanners
        test_ssl_scanner()
        test_headers_scanner()
        test_vulnerability_scanner()
        
        # Test comprehensive scanner
        test_comprehensive_scanner()
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

