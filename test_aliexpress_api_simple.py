#!/usr/bin/env python3
"""
Test if AliExpress API code can be initialized and used
"""

import sys
import os

# Check if aliexpress_api is available
try:
    from aliexpress_api import AliexpressApi, models
    print("✓ aliexpress_api library is installed")
    API_AVAILABLE = True
except ImportError as e:
    print("✗ aliexpress_api library NOT installed")
    print(f"   Error: {e}")
    print("\n   To install, you need to find a working AliExpress API library.")
    print("   The original python-aliexpress-api repository seems to be unavailable.")
    API_AVAILABLE = False

print("\n" + "="*70)

if API_AVAILABLE:
    # Try to initialize the API
    try:
        from product_fetcher import AliExpressProductFetcher
        
        print("Testing AliExpressProductFetcher initialization...")
        fetcher = AliExpressProductFetcher()
        print("✓ AliExpress API initialized successfully")
        
        # Try a simple search
        print("\nTesting product search for 'phone case'...")
        results = fetcher.search_products("phone case", max_results=3)
        
        print(f"\n✓ Found {len(results)} products:")
        for i, product in enumerate(results, 1):
            print(f"\n  {i}. {product['title'][:60]}")
            print(f"     Price: {product['price']}")
            print(f"     URL: {product.get('affiliate_url', 'N/A')[:80]}...")
        
    except Exception as e:
        print(f"\n✗ Error during API test: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\nCannot test API - library not installed")
    print("\nAlternatives:")
    print("1. Find and install a working AliExpress API Python library")
    print("2. Use direct HTTP requests to AliExpress API endpoints")
    print("3. Contact AliExpress to get their official Python SDK")

print("\n" + "="*70)
