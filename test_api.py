#!/usr/bin/env python3
"""
בדיקה מהירה של AliExpress API
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_credentials():
    """בדיקת credentials"""
    print("=" * 60)
    print("🔑 בדיקת Credentials של AliExpress")
    print("=" * 60)
    
    app_key = os.getenv('ALIEXPRESS_APP_KEY')
    app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
    callback_url = os.getenv('ALIEXPRESS_CALLBACK_URL')
    
    if app_key:
        print(f"✅ App Key: {app_key}")
    else:
        print("❌ App Key לא מוגדר!")
        
    if app_secret:
        print(f"✅ App Secret: {app_secret[:15]}...")
    else:
        print("❌ App Secret לא מוגדר!")
        
    if callback_url:
        print(f"✅ Callback URL: {callback_url}")
    else:
        print("⚠️  Callback URL לא מוגדר")
    
    print()
    return bool(app_key and app_secret)


def test_fetcher():
    """בדיקת ProductFetcher של AliExpress"""
    print("=" * 60)
    print("🧪 בדיקת AliExpressFetcher")
    print("=" * 60)
    
    try:
        from product_fetcher import get_fetcher
        
        # יצירת fetcher לAliExpress
        fetcher = get_fetcher('aliexpress')
        
        if fetcher:
            print(f"✅ Fetcher נוצר בהצלחה: {type(fetcher).__name__}")
            print(f"   App Key: {fetcher.app_key}")
            print(f"   יש App Secret: {'✅' if fetcher.app_secret else '❌'}")
            return True
        else:
            print("❌ לא הצלחנו ליצור Fetcher")
            return False
            
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False


def test_product_fetch():
    """בדיקת משיכת מוצר לדוגמה"""
    print("\n" + "=" * 60)
    print("🛒 ניסיון למשוך מוצר לדוגמה")
    print("=" * 60)
    
    try:
        from product_fetcher import get_fetcher
        
        fetcher = get_fetcher('aliexpress')
        
        # נסה למשוך מוצר עם URL לדוגמה
        test_url = "https://www.aliexpress.com/item/1005003.html"
        
        print(f"🔍 מנסה למשוך מוצר מ: {test_url}")
        product = fetcher.fetch_product_info(test_url)
        
        if product:
            print(f"\n✅ המוצר נמשך בהצלחה!")
            print(f"   כותרת: {product.get('title', 'N/A')[:50]}...")
            print(f"   מחיר: {product.get('price', 'N/A')}")
            print(f"   URL: {product.get('url', 'N/A')[:50]}...")
            return True
        else:
            print("⚠️  לא נמצא מוצר (ייתכן שה-URL לא תקין)")
            return False
            
    except Exception as e:
        print(f"⚠️  שגיאה: {e}")
        print("   (זה נורמלי אם ה-URL לא תקין)")
        return False


def main():
    """פונקציה ראשית"""
    print("\n" + "=" * 60)
    print("🚀 בדיקת AliExpress API Integration")
    print("=" * 60)
    print()
    
    # בדיקת credentials
    has_credentials = check_credentials()
    
    if not has_credentials:
        print("\n⚠️  חסרים Credentials! הוסף אותם ב-file .env")
        print("   ALIEXPRESS_APP_KEY=your_app_key")
        print("   ALIEXPRESS_APP_SECRET=your_app_secret")
        return
    
    # בדיקת fetcher
    fetcher_works = test_fetcher()
    
    if not fetcher_works:
        print("\n❌ Fetcher לא עובד. בדוק את ה-credentials")
        return
    
    # בדיקת משיכת מוצר (אופציונלי)
    print("\nהאם תרצה לנסות למשוך מוצר לדוגמה? (y/n): ", end="")
    try:
        answer = input().lower()
        if answer == 'y':
            test_product_fetch()
    except:
        pass
    
    print("\n" + "=" * 60)
    print("✅ הבדיקה הושלמה!")
    print("=" * 60)
    print("\n📋 הצעדים הבאים:")
    print("   1. גש ל: http://localhost:5000/callback-config")
    print("   2. העתק את ה-Callback URL")
    print("   3. הוסף אותו ב-AliExpress Portal")
    print("   4. התחל להוסיף מוצרים!")
    print()


if __name__ == '__main__':
    main()
