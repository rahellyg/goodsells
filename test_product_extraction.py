"""
סקריפט בדיקה לחילוץ מוצר מקישור
Test script for product extraction from URL
"""
# -*- coding: utf-8 -*-
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

from product_fetcher import get_fetcher


def test_product_extraction(url: str, store: str = 'amazon'):
    """בדיקת חילוץ מוצר מקישור"""
    print("=" * 60)
    print("Product Extraction Test")
    print("=" * 60)
    print(f"\n[URL] {url}")
    print(f"[STORE] {store}\n")
    
    # Get fetcher
    fetcher = get_fetcher(store)
    
    # Fetch product
    product = fetcher.fetch_product_by_url(url)
    
    if not product:
        print("\n[X] Failed to extract product information")
        return None
    
    # Display results
    print("\n" + "=" * 60)
    print("EXTRACTED PRODUCT INFORMATION")
    print("=" * 60)
    print(f"\n📦 Title: {product.get('title', 'N/A')}")
    print(f"💰 Price: {product.get('price', 'N/A')}")
    
    if product.get('original_price'):
        print(f"💵 Original Price: {product.get('original_price')}")
    
    if product.get('discount'):
        print(f"🎯 Discount: {product.get('discount')}")
    
    print(f"⭐ Rating: {product.get('rating', 0)}")
    print(f"📝 Reviews: {product.get('reviews_count', 0)}")
    
    if product.get('description'):
        desc = product.get('description', '')
        if len(desc) > 150:
            desc = desc[:150] + "..."
        print(f"📄 Description: {desc}")
    
    if product.get('image_url'):
        print(f"🖼️  Image: {product.get('image_url')[:80]}...")
    else:
        print(f"🖼️  Image: Not found (will use placeholder)")
    
    print(f"🔗 Affiliate URL: {product.get('affiliate_url', 'N/A')}")
    
    print("\n" + "=" * 60)
    
    return product


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test product extraction from URL')
    parser.add_argument('url', help='Product URL to extract')
    parser.add_argument('--store', default='amazon', choices=['amazon', 'aliexpress'],
                       help='Store type (default: amazon)')
    
    args = parser.parse_args()
    
    test_product_extraction(args.url, args.store)
