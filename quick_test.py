#!/usr/bin/env python3
"""
בדיקה מהירה - האם API עובד?
"""
from product_fetcher import get_fetcher

print("\n" + "=" * 70)
print("🧪 בדיקה מהירה: האם AliExpress API עובד?")
print("=" * 70)
print()

# צור fetcher
fetcher = get_fetcher('aliexpress')

print("\n" + "=" * 70)
print("🔍 מנסה למשוך מוצר לדוגמה...")
print("=" * 70)
print()

# נסה URL לדוגמה
test_url = "https://www.aliexpress.com/item/1005003457890123.html"

product = fetcher.fetch_product_by_url(test_url)

print("\n" + "=" * 70)
print("📊 תוצאה:")
print("=" * 70)

if product:
    print(f"✅ הצלחה! נמשך מוצר:")
    print(f"   • כותרת: {product.get('title', 'N/A')[:60]}...")
    print(f"   • מחיר: {product.get('price', 'N/A')}")
else:
    print("❌ לא הצלחנו למשוך מוצר")

print()
print("=" * 70)
print("💡 איך לדעת אם API עובד?")
print("=" * 70)
print()
print("תראה אחת מההודעות האלה:")
print()
print("  🔵 [API MODE] - אם רואה את זה = API מנסה לעבוד")
print("     ↓")
print("  ✅ [API SUCCESS] - API עובד! 🎉")
print()
print("  או:")
print()
print("  ⚠️  [API FAILED] - API לא עובד")
print("     ↓")
print("  🟡 [SCRAPING MODE] - עובר אוטומטית ל-scraping")
print()
print("=" * 70)
print()
