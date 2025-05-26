#!/usr/bin/env python3
"""
Simple test script for the IBKR Trading API
Run this script to test the API endpoints locally
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_status():
    """Test the status endpoint"""
    print("🔍 Testing status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_home():
    """Test the home endpoint"""
    print("\n🏠 Testing home endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_account():
    """Test the account endpoint"""
    print("\n💰 Testing account endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/account")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_buy_order():
    """Test placing a buy order (paper trading recommended)"""
    print("\n📈 Testing buy order endpoint...")
    
    # Example buy order - MODIFY THESE VALUES FOR YOUR TESTING
    order_data = {
        "symbol": "AAPL",
        "quantity": 1,
        "order_type": "MARKET"
    }
    
    print(f"Order data: {json.dumps(order_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/buy",
            headers={"Content-Type": "application/json"},
            json=order_data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_sell_order():
    """Test placing a sell order (paper trading recommended)"""
    print("\n📉 Testing sell order endpoint...")
    
    # Example sell order - MODIFY THESE VALUES FOR YOUR TESTING
    order_data = {
        "symbol": "AAPL",
        "quantity": 1,
        "order_type": "LIMIT",
        "price": 200.00  # Set a high price to avoid accidental execution
    }
    
    print(f"Order data: {json.dumps(order_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/sell",
            headers={"Content-Type": "application/json"},
            json=order_data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting IBKR Trading API Tests")
    print("=" * 50)
    
    # Test basic endpoints first
    tests = [
        ("Status", test_status),
        ("Home", test_home),
        ("Account", test_account),
    ]
    
    # Ask user if they want to test trading endpoints
    print("\n⚠️  WARNING: The following tests will attempt to place actual orders!")
    print("Make sure you're using a paper trading account or are prepared for real trades.")
    test_trading = input("Do you want to test buy/sell endpoints? (y/N): ").lower().strip() == 'y'
    
    if test_trading:
        tests.extend([
            ("Buy Order", test_buy_order),
            ("Sell Order", test_sell_order),
        ])
    
    # Run tests
    results = []
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 