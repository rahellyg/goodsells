#!/usr/bin/env python3
"""
סקריפט לתיקון קישורי Amazon ב-products.json
מוסיף את ה-associate tag בפורמט הנכון
"""
import json
from urllib.parse import urlparse, parse_qs, quote

def fix_amazon_affiliate_url(url: str, associate_tag: str = "goodsells02-20") -> str:
    """תיקון קישור Amazon affiliate"""
    # בדיקה אם זה לינק Amazon
    if 'amazon.com' not in url and 'amzn.to' not in url:
        return url
    
    # חילוץ ASIN מה-URL
    asin = None
    if '/dp/' in url:
        parts = url.split('/dp/')
        if len(parts) > 1:
            asin = parts[1].split('/')[0].split('?')[0]
    elif '/gp/product/' in url:
        parts = url.split('/gp/product/')
        if len(parts) > 1:
            asin = parts[1].split('/')[0].split('?')[0]
    
    if not asin or len(asin) != 10:
        print(f"  [!] Could not extract ASIN from: {url}")
        return url
    
    # בניית URL נקי עם tag
    new_url = f"https://www.amazon.com/dp/{asin}?tag={associate_tag}"
    return new_url

def main():
    """תיקון כל הלינקים ב-products.json"""
    # קריאת הקובץ
    with open('products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[*] Found {len(data['products'])} products")
    
    # תיקון כל מוצר
    fixed_count = 0
    for product in data['products']:
        old_url = product.get('affiliate_url', '')
        
        # תיקון רק עבור Amazon
        if 'amazon.com' in old_url or 'amzn.to' in old_url:
            new_url = fix_amazon_affiliate_url(old_url)
            if new_url != old_url:
                product['affiliate_url'] = new_url
                fixed_count += 1
                print(f"\n[✓] Fixed: {product['title'][:50]}...")
                print(f"    Old: {old_url}")
                print(f"    New: {new_url}")
    
    # שמירת הקובץ
    if fixed_count > 0:
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n[✓] Fixed {fixed_count} Amazon product links")
        print(f"[✓] Saved to products.json")
    else:
        print("\n[*] No Amazon links needed fixing")

if __name__ == '__main__':
    main()
