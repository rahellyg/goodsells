#!/usr/bin/env python3
"""
AliExpress Affiliate Integration Example

This script demonstrates how to use the AliExpress affiliate callback system.
"""
import requests
import json

# Your server URL (change to your actual domain in production)
BASE_URL = "http://localhost:5000"

# Or use your ngrok URL for testing:
# BASE_URL = "https://your-ngrok-url.ngrok.io"


def get_callback_urls():
    """Get the callback URLs from your server"""
    try:
        response = requests.get(f"{BASE_URL}/api/config/callback-url")
        data = response.json()
        
        print("=" * 60)
        print("📋 Your AliExpress Callback URLs")
        print("=" * 60)
        print(f"\n✓ Callback URL:")
        print(f"  {data['aliexpress']['callback']}")
        print(f"\n✓ Webhook URL:")
        print(f"  {data['aliexpress']['webhook']}")
        
        if data.get('is_local'):
            print(f"\n⚠️  Running locally!")
            print(f"   Use ngrok for testing: ngrok http 5000")
        
        print("\n" + "=" * 60)
        print("📋 Copy these URLs to your AliExpress affiliate portal")
        print("=" * 60)
        
        return data
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_callback():
    """Test the callback endpoint with sample data"""
    try:
        # Sample callback data (simulating what AliExpress would send)
        test_data = {
            'order_id': 'TEST123456',
            'commission': '5.50',
            'status': 'paid',
            'product_id': '4000123456789',
            'timestamp': '2026-01-29T10:00:00Z'
        }
        
        print("\n🧪 Testing callback endpoint...")
        print(f"Sending test data: {json.dumps(test_data, indent=2)}")
        
        # Test POST request
        response = requests.post(
            f"{BASE_URL}/api/aliexpress/callback",
            json=test_data
        )
        
        if response.status_code == 200:
            print("✓ Callback test successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Callback test failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error testing callback: {e}")


def test_webhook():
    """Test the webhook endpoint"""
    try:
        # Sample webhook data
        test_data = {
            'event_type': 'order.paid',
            'order_id': 'WEBHOOK123',
            'amount': '25.99',
            'commission': '2.60'
        }
        
        print("\n🔔 Testing webhook endpoint...")
        print(f"Sending webhook data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/aliexpress/webhook",
            json=test_data
        )
        
        if response.status_code == 200:
            print("✓ Webhook test successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Webhook test failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error testing webhook: {e}")


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("AliExpress Affiliate Integration Test")
    print("=" * 60)
    
    # Get callback URLs
    urls = get_callback_urls()
    
    if not urls:
        print("\n❌ Could not fetch callback URLs.")
        print("   Make sure your Flask app is running!")
        return
    
    # Ask user if they want to test
    print("\n")
    test = input("Do you want to test the callbacks? (y/n): ").lower()
    
    if test == 'y':
        test_callback()
        test_webhook()
        print("\n✓ Tests completed! Check your server logs.")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Copy the callback URLs above")
    print("2. Go to https://portals.aliexpress.com/")
    print("3. Add the callback URL to your app settings")
    print("4. Test with real AliExpress callbacks")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
