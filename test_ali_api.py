#!/usr/bin/env python3
"""
Test AliExpress API directly
"""

# Install first: pip install git+https://github.com/python-aliexpress-api/python-aliexpress-api.git

try:
    from aliexpress_api import AliexpressApi, models
    
    ALI_APP_KEY = "526322"
    ALI_APP_SECRET = "qMAJARlyy0zjzcF62yrvTvTYxwtH9Ix1"
    TRACKING_ID = "goodsles"  # affiliate tracking id
    
    print("="  * 70)
    print("Testing AliExpress API")
    print("=" * 70)
    
    aliexpress = AliexpressApi(
        ALI_APP_KEY,
        ALI_APP_SECRET,
        models.Language.EN,
        models.Currency.USD,
        TRACKING_ID
    )
    
    def get_aliexpress_products(keyword):
        response = aliexpress.get_products(
            keywords=keyword,
            page_no=1,
            page_size=10
        )
        print(f"\nFound {len(response.products)} products for '{keyword}':\n")
        
        for i, product in enumerate(response.products[:5], 1):
            print(f"{i}. {product.product_title}")
            print(f"   Price: ${product.sale_price}")
            print(f"   URL: {product.product_detail_url[:80]}...")
            print()
        
        return response.products
    
    # Test
    products = get_aliexpress_products("phone case")
    
except ImportError as e:
    print("ERROR: aliexpress_api not installed!")
    print(f"\nInstall with:")
    print("  pip install git+https://github.com/python-aliexpress-api/python-aliexpress-api.git")
    print(f"\nError: {e}")
except Exception as e:
    print(f"ERROR: {e}")
