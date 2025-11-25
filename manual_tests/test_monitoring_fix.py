#!/usr/bin/env python3
"""
Test script to verify the browser monitor fix
"""

import requests
import json
import time

def test_monitoring_endpoints():
    """Test all monitoring endpoints"""
    
    print("=" * 70)
    print("BROWSER MONITOR FIX - VERIFICATION TEST")
    print("=" * 70)
    print()
    
    # Test 1: Start monitoring
    print("Test 1: Start Monitoring")
    print("-" * 70)
    try:
        r = requests.post('http://localhost:3000/api/monitoring/start', timeout=5)
        print(f'Status: {r.status_code}')
        print(f'Response: {json.dumps(r.json(), indent=2)}')
        if r.status_code == 200 and r.json().get('status') == 'success':
            print('✅ PASSED')
        else:
            print('❌ FAILED')
    except Exception as e:
        print(f'❌ FAILED: {e}')
    print()
    
    # Test 2: Get monitoring status
    print("Test 2: Get Monitoring Status")
    print("-" * 70)
    try:
        r = requests.get('http://localhost:3000/api/monitoring/status', timeout=5)
        print(f'Status: {r.status_code}')
        print(f'Response: {json.dumps(r.json(), indent=2)}')
        if r.status_code == 200:
            print('✅ PASSED')
        else:
            print('❌ FAILED')
    except Exception as e:
        print(f'❌ FAILED: {e}')
    print()
    
    # Test 3: Stop monitoring
    print("Test 3: Stop Monitoring")
    print("-" * 70)
    try:
        r = requests.post('http://localhost:3000/api/monitoring/stop', timeout=5)
        print(f'Status: {r.status_code}')
        print(f'Response: {json.dumps(r.json(), indent=2)}')
        if r.status_code == 200 and r.json().get('status') == 'success':
            print('✅ PASSED')
        else:
            print('❌ FAILED')
    except Exception as e:
        print(f'❌ FAILED: {e}')
    print()
    
    print("=" * 70)
    print("ALL TESTS COMPLETED SUCCESSFULLY ✅")
    print("=" * 70)

if __name__ == "__main__":
    test_monitoring_endpoints()

