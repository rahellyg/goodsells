"""
דוגמה לשימוש במערכת
Example usage of the video generation system
"""
# -*- coding: utf-8 -*-
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

from product_fetcher import get_fetcher
from video_generator import VideoGenerator


def example_basic_usage():
    """דוגמה בסיסית ליצירת סרטון"""
    print("=" * 50)
    print("דוגמה: יצירת סרטון שיווק")
    print("=" * 50)
    
    # 1. משיכת מוצר
    print("\n[1] משיכת מוצר...")
    fetcher = get_fetcher('amazon')
    products = fetcher.search_products('טלפון חכם', max_results=1)
    
    if not products:
        print("[X] לא נמצאו מוצרים")
        return
    
    product = products[0]
    print(f"[OK] נמצא מוצר: {product['title']}")
    print(f"     מחיר: {product['price']}")
    print(f"     דירוג: {product['rating']} כוכבים")
    
    # 2. יצירת סרטון
    print("\n[2] יצירת סרטון...")
    generator = VideoGenerator()
    video_path = generator.create_product_video(product)
    
    if video_path:
        print(f"\n[OK] הסרטון נוצר בהצלחה!")
        print(f"     מיקום: {video_path}")
        print(f"     קישור שותפים: {product['affiliate_url']}")
    else:
        print("[X] שגיאה ביצירת הסרטון")


def example_multiple_products():
    """דוגמה ליצירת מספר סרטונים"""
    print("=" * 50)
    print("דוגמה: יצירת מספר סרטונים")
    print("=" * 50)
    
    # חיפוש מספר מוצרים
    fetcher = get_fetcher('amazon')
    products = fetcher.search_products('גאדג\'טים', max_results=3)
    
    print(f"\n[OK] נמצאו {len(products)} מוצרים")
    
    # יצירת סרטון לכל מוצר
    generator = VideoGenerator()
    videos = []
    
    for i, product in enumerate(products, 1):
        print(f"\n[VIDEO] [{i}/{len(products)}] יוצר סרטון: {product['title']}")
        video_path = generator.create_product_video(product)
        if video_path:
            videos.append(video_path)
    
    print(f"\n[OK] נוצרו {len(videos)} סרטונים:")
    for video in videos:
        print(f"   • {video}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'multiple':
        example_multiple_products()
    else:
        example_basic_usage()
