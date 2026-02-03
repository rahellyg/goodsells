#!/usr/bin/env python3
"""
Test if affiliate tracking is working for commission
"""

from product_fetcher import AliExpressProductFetcher
import re

print("="*70)
print("TESTING AFFILIATE COMMISSION TRACKING")
print("="*70)

try:
    fetcher = AliExpressProductFetcher()
    print(f"\n✓ API Initialized")
    print(f"  Tracking ID: {fetcher.affiliate_tracking}")
    print(f"  App Key: {fetcher.app_key}")
    
    print("\n" + "="*70)
    print("Searching for products...")
    print("="*70)
    
    products = fetcher.search_products('phone', max_results=2)
    
    if products:
        print(f"\n✓ Found {len(products)} products\n")
        
        for i, product in enumerate(products, 1):
            print(f"\n--- Product {i} ---")
            print(f"Title: {product['title'][:50]}...")
            print(f"Price: {product['price']}")
            print(f"\nAffiliate URL:")
            print(product['affiliate_url'])
            
            # Analyze the URL
            url = product['affiliate_url']
            
            # Check for tracking parameters
            has_tracking = False
            tracking_params = []
            
            if 'aff_trace_key' in url:
                tracking_params.append('aff_trace_key')
                has_tracking = True
            
            if fetcher.affiliate_tracking in url:
                tracking_params.append(f'tracking_id: {fetcher.affiliate_tracking}')
                has_tracking = True
            
            if 'pdp_npi' in url:
                tracking_params.append('pdp_npi (product detail page tracking)')
                has_tracking = True
            
            # Check for AliExpress affiliate URL structure
            if 's.click.aliexpress.com' in url or 'aff_short_key' in url:
                tracking_params.append('AliExpress affiliate link')
                has_tracking = True
            
            print(f"\n{'='*50}")
            if has_tracking:
                print("✓ TRACKING DETECTED!")
                print(f"  Parameters found: {', '.join(tracking_params)}")
                print("\n✓ This link SHOULD generate commission!")
            else:
                print("✗ WARNING: NO TRACKING DETECTED!")
                print("\n✗ This link might NOT generate commission!")
                print("\nPossible issues:")
                print("  1. Tracking ID not registered with AliExpress")
                print("  2. API credentials not linked to affiliate account")
                print("  3. Need to apply for AliExpress Affiliate Program")
            print("="*50)
    else:
        print("\n✗ No products found")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("IMPORTANT NOTES:")
print("="*70)
print("""
To get commission from AliExpress, you MUST:

1. ✓ Register for AliExpress Affiliate Program
   → Go to: https://portals.aliexpress.com/

2. ✓ Get approved as an affiliate

3. ✓ Link your API credentials to your affiliate account
   → Your Tracking ID must be registered in your account

4. ✓ Use the correct API keys from your affiliate dashboard
   → Current App Key: 526322 (check if this is YOUR key!)
   → Current Tracking ID: goodsles (check if this is YOUR ID!)

5. ✓ The API should return affiliate links automatically
   → Links should contain tracking parameters

If you're using DEFAULT credentials (526322/goodsles),
you're probably NOT getting commission!

ACTION REQUIRED:
→ Replace with YOUR OWN credentials in .env file:
  ALIEXPRESS_APP_KEY=your_app_key
  ALIEXPRESS_APP_SECRET=your_app_secret
  ALIEXPRESS_AFFILIATE_TRACKING=your_tracking_id
""")
print("="*70)
