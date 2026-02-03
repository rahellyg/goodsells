#!/usr/bin/env python3
"""
בדיקה - איך נראה ה-affiliate link?
"""
from product_fetcher import get_fetcher
import json

print("\n" + "=" * 70)
print("🔗 בדיקת Affiliate Links - AliExpress")
print("=" * 70)
print()

# צור fetcher
fetcher = get_fetcher('aliexpress')

print("📋 מידע על ה-fetcher:")
print(f"   App Key: {fetcher.app_key}")
print(f"   App Secret: {'✓' if fetcher.app_secret else '✗'}")
print(f"   Affiliate Tracking: {fetcher.affiliate_tracking if fetcher.affiliate_tracking else '(לא מוגדר)'}")
print()

# דוגמה של URL מוצר
product_url = "https://www.aliexpress.com/item/1005003457890123.html"
print(f"🔍 URL מקורי של מוצר:")
print(f"   {product_url}")
print()

# נסה למשוך את המוצר
print("📦 מושך מידע על המוצר...")
product = fetcher.fetch_product_by_url(product_url)

if product:
    print()
    print("=" * 70)
    print("✅ המוצר נמשך! הנה ה-affiliate link:")
    print("=" * 70)
    print()
    
    affiliate_url = product.get('affiliate_url') or product.get('url', '')
    
    print(f"🔗 Affiliate URL (זה מה שהלקוח לוחץ עליו):")
    print(f"   {affiliate_url}")
    print()
    
    # בדוק אם יש tracking parameters
    if 'aff_trace_key' in affiliate_url or 'aff_platform' in affiliate_url:
        print("✅ ה-URL כולל tracking parameters - תקבל commission!")
    elif fetcher.app_key in affiliate_url or 'tag=' in affiliate_url:
        print("✅ ה-URL כולל את ה-affiliate tag שלך - תקבל commission!")
    else:
        print("⚠️  ה-URL לא כולל tracking - צריך להוסיף ALIEXPRESS_AFFILIATE_TRACKING ל-.env")
    
    print()
    print("📊 כל השדות של המוצר:")
    print("-" * 70)
    for key, value in product.items():
        if key == 'description':
            print(f"   {key}: {str(value)[:50]}...")
        else:
            print(f"   {key}: {value}")

print()
print("=" * 70)
print("💡 איך זה עובד:")
print("=" * 70)
print("""
1. המערכת מושכת את המוצר מ-AliExpress
2. אם יש ALIEXPRESS_AFFILIATE_TRACKING ב-.env - הוא מוסיף אותו ל-URL
3. כשלקוח לוחץ על "קנה עכשיו" - הוא עובר ל-AliExpress עם ה-tracking שלך
4. AliExpress רואה את ה-tracking ID ושולח לך callback כשיש מכירה
5. אתה מקבל commission! 💰

⚠️  כרגע: המערכת לא משתמשת ב-API אלא ב-web scraping
   זה אומר: ה-URL הוא פשוט קישור ישיר ל-AliExpress
   
   כדי לקבל commissions צריך להוסיף:
   ALIEXPRESS_AFFILIATE_TRACKING=your_tracking_id
""")
print("=" * 70)
print()
