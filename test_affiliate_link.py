"""
סקריפט בדיקה להוספת מוצר דרך קישור שותפים
Test script for adding product via affiliate link
"""
# -*- coding: utf-8 -*-
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

from product_fetcher import get_fetcher


def test_affiliate_link(affiliate_url: str):
    """בדיקת חילוץ מוצר מקישור שותפים"""
    print("=" * 60)
    print("Affiliate Link Test")
    print("=" * 60)
    print(f"\n[AFFILIATE LINK] {affiliate_url}\n")
    
    # Get fetcher
    fetcher = get_fetcher('amazon')
    
    try:
        # Fetch product using affiliate link
        print("[FETCH] Fetching product from affiliate link...")
        product = fetcher.fetch_product_by_url(affiliate_url)
        
        if product:
            print("\n" + "=" * 60)
            print("PRODUCT EXTRACTED SUCCESSFULLY")
            print("=" * 60)
            print(f"\n📦 Title: {product.get('title', 'N/A')}")
            print(f"💰 Price: {product.get('price', 'N/A')}")
            
            if product.get('original_price'):
                print(f"💵 Original Price: {product.get('original_price')}")
            
            if product.get('discount'):
                print(f"🎯 Discount: {product.get('discount')}")
            
            print(f"⭐ Rating: {product.get('rating', 0)}")
            print(f"📝 Reviews: {product.get('reviews_count', 0)}")
            
            if product.get('affiliate_url'):
                print(f"\n🔗 New Affiliate URL (with your tag):")
                print(f"   {product.get('affiliate_url')}")
            
            if product.get('video_url'):
                print(f"\n🎬 Product Video URL:")
                print(f"   {product.get('video_url')}")
            
            print("\n" + "=" * 60)
            print("[OK] Product extracted successfully from affiliate link!")
            print("=" * 60)
            
            return product
        else:
            print("\n[X] Failed to extract product from affiliate link")
            return None
    
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test affiliate link extraction')
    parser.add_argument('url', help='Affiliate link URL to test')
    
    args = parser.parse_args()
    
    test_affiliate_link(args.url)
