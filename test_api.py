#!/usr/bin/env python3
"""
Simple test script to verify the GradeMate API is working
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Root endpoint failed: {e}")
        return False

def test_marking_schemes():
    """Test marking schemes endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/marking-schemes")
        print(f"Marking schemes: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Marking schemes failed: {e}")
        return False

def test_answer_sheets():
    """Test answer sheets endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/answer-sheets")
        print(f"Answer sheets: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Answer sheets failed: {e}")
        return False

def test_statistics():
    """Test statistics endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/statistics")
        print(f"Statistics: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Statistics failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing GradeMate API...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Marking Schemes", test_marking_schemes),
        ("Answer Sheets", test_answer_sheets),
        ("Statistics", test_statistics),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
