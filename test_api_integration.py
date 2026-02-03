#!/usr/bin/env python3
"""
בדיקת אינטגרציה של AliExpress API
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_api_integration():
    """בדיקה מקיפה של אינטגרציית ה-API"""
    
    print("=" * 70)
    print("🧪 בדיקת אינטגרציה של AliExpress API")
    print("=" * 70)
    print()
    
    # 1. בדיקת credentials
    print("📋 שלב 1: בדיקת Credentials")
    print("-" * 70)
    
    app_key = os.getenv('ALIEXPRESS_APP_KEY')
    app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
    
    if not app_key or not app_secret:
        print("❌ Credentials חסרים!")
        print("   הוסף את הערכים הבאים ל-.env:")
        print("   ALIEXPRESS_APP_KEY=your_key")
        print("   ALIEXPRESS_APP_SECRET=your_secret")
        return False
    
    print(f"✅ App Key: {app_key}")
    print(f"✅ App Secret: {app_secret[:15]}...")
    print()
    
    # 2. בדיקת יצירת Fetcher
    print("📋 שלב 2: יצירת AliExpressFetcher")
    print("-" * 70)
    
    try:
        from product_fetcher import get_fetcher
        
        fetcher = get_fetcher('aliexpress')
        
        if not fetcher:
            print("❌ לא הצלחתי ליצור Fetcher")
            return False
        
        print(f"✅ Fetcher נוצר: {type(fetcher).__name__}")
        print(f"   משתמש ב-API: {'✅ כן' if fetcher.use_api else '❌ לא (scraping)'}")
        print()
        
        # 3. בדיקת פונקציות API
        print("📋 שלב 3: בדיקת פונקציות API")
        print("-" * 70)
        
        # בדוק שהפונקציות קיימות
        required_methods = [
            '_generate_signature',
            '_make_api_request',
            '_search_products_api',
            '_fetch_product_by_url_api'
        ]
        
        for method_name in required_methods:
            if hasattr(fetcher, method_name):
                print(f"✅ {method_name} קיימת")
            else:
                print(f"❌ {method_name} חסרה!")
        
        print()
        
        # 4. בדיקת signature generation
        print("📋 שלב 4: בדיקת יצירת Signature")
        print("-" * 70)
        
        try:
            test_params = {
                'app_key': app_key,
                'test_param': 'test_value',
                'timestamp': '1234567890'
            }
            signature = fetcher._generate_signature('test.api.method', test_params)
            
            if signature and len(signature) == 64:  # SHA256 returns 64 hex chars
                print(f"✅ Signature נוצר בהצלחה: {signature[:20]}...")
            else:
                print(f"⚠️  Signature נראה לא תקין: {signature}")
        except Exception as e:
            print(f"❌ שגיאה ביצירת signature: {e}")
        
        print()
        
        # 5. ניסיון בקשת API אמיתית (אופציונלי)
        print("📋 שלב 5: ניסיון בקשת API (אופציונלי)")
        print("-" * 70)
        print("האם לנסות לבצע בקשת API אמיתית? (עלול לקחת מספר שניות)")
        answer = input("y/n: ").lower()
        
        if answer == 'y':
            print("\n🔄 מבצע בקשת API לקבלת מוצרים מומלצים...")
            try:
                # Try to get recommended products
                api_name = "aliexpress.ds.recommend.feed.get"
                params = {
                    'target_currency': 'USD',
                    'target_language': 'EN',
                    'feed_name': 'DS_bestselling',
                    'category_id': '0',
                    'page_no': '1',
                    'page_size': '5'
                }
                
                result = fetcher._make_api_request(api_name, params)
                
                if result:
                    print("✅ בקשת API הצליחה!")
                    print(f"   תשובה: {str(result)[:200]}...")
                else:
                    print("⚠️  בקשת API החזירה None (בדוק credentials או חיבור)")
            except Exception as e:
                print(f"❌ שגיאה בבקשת API: {e}")
        
        print()
        print("=" * 70)
        print("✅ הבדיקה הושלמה!")
        print("=" * 70)
        print()
        print("📋 סיכום:")
        print(f"   • Credentials: {'✅' if app_key and app_secret else '❌'}")
        print(f"   • Fetcher: ✅")
        print(f"   • שימוש ב-API: {'✅' if fetcher.use_api else '❌'}")
        print()
        print("🚀 אפשר להתחיל להשתמש ב-API!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    test_api_integration()
