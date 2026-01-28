"""
סקריפט ראשי ליצירת סרטוני שיווק אוטומטיים
Main Script for Automated Marketing Video Creation
"""
# -*- coding: utf-8 -*-
import os
import sys

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    try:
        # Try to set console to UTF-8
        os.system('chcp 65001 >nul 2>&1')
        # Also set stdout/stderr encoding
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        else:
            # Fallback for older Python versions
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

from dotenv import load_dotenv
from product_fetcher import get_fetcher
from video_generator import VideoGenerator
import argparse

load_dotenv()


def create_videos_from_keywords(keywords: str, store: str = 'amazon', count: int = 5):
    """יצירת סרטונים ממילות מפתח"""
    print(f"🔍 Searching for products: '{keywords}' on {store}")
    
    # משיכת מוצרים
    fetcher = get_fetcher(store)
    products = fetcher.search_products(keywords, max_results=count)
    
    if not products:
        print("[X] No products found")
        return
    
    print(f"[OK] Found {len(products)} products")
    
    # יצירת סרטונים
    generator = VideoGenerator()
    created_videos = []
    
    for i, product in enumerate(products, 1):
        print(f"\n[VIDEO] [{i}/{len(products)}] Processing: {product.get('title', 'Unknown')}")
        video_path = generator.create_product_video(product)
        
        if video_path:
            created_videos.append({
                'product': product.get('title', 'Unknown'),
                'video_path': video_path,
                'affiliate_url': product.get('affiliate_url', '')
            })
    
    # סיכום
    print("\n" + "="*50)
    print("[SUMMARY]")
    print("="*50)
    print(f"[OK] Created {len(created_videos)} videos:")
    for item in created_videos:
        print(f"  • {item['product']}")
        print(f"    Video: {item['video_path']}")
        print(f"    Affiliate: {item['affiliate_url']}")
        print()
    
    return created_videos


def create_video_from_url(product_url: str, store: str = 'amazon'):
    """יצירת סרטון ממוצר בודד לפי URL"""
    print(f"🔗 Fetching product from URL: {product_url}")
    
    # משיכת מוצר
    fetcher = get_fetcher(store)
    product = fetcher.fetch_product_by_url(product_url)
    
    if not product:
        print("[X] Failed to fetch product")
        return None
    
    print(f"[OK] Product found: {product.get('title', 'Unknown')}")
    
    # יצירת סרטון
    generator = VideoGenerator()
    video_path = generator.create_product_video(product)
    
    if video_path:
        print(f"\n[OK] Video created: {video_path}")
        print(f"[LINK] Affiliate URL: {product.get('affiliate_url', '')}")
    
    return video_path


def main():
    """פונקציה ראשית"""
    parser = argparse.ArgumentParser(
        description='מערכת ליצירת סרטוני שיווק אוטומטיים',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
דוגמאות שימוש:
  # חיפוש מוצרים לפי מילות מפתח
  python main.py --keywords "טלפון חכם" --store amazon --count 3
  
  # יצירת סרטון ממוצר בודד
  python main.py --url "https://amazon.com/dp/EXAMPLE123" --store amazon
  
  # יצירת סרטונים מ-AliExpress
  python main.py --keywords "שעון חכם" --store aliexpress --count 5
        """
    )
    
    parser.add_argument(
        '--keywords',
        type=str,
        help='מילות מפתח לחיפוש מוצרים'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        help='URL של מוצר ספציפי'
    )
    
    parser.add_argument(
        '--store',
        type=str,
        default='amazon',
        choices=['amazon', 'aliexpress'],
        help='חנות שותפים (default: amazon)'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='מספר מוצרים ליצירה (default: 5)'
    )
    
    args = parser.parse_args()
    
    # בדיקת פרמטרים
    if not args.keywords and not args.url:
        parser.print_help()
        print("\n[X] Error: You must provide either --keywords or --url")
        sys.exit(1)
    
    # יצירת סרטונים
    if args.url:
        create_video_from_url(args.url, args.store)
    else:
        create_videos_from_keywords(args.keywords, args.store, args.count)


if __name__ == '__main__':
    main()
