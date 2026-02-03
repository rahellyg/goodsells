#!/usr/bin/env python3
"""
בדיקה פשוטה לוודא שה-affiliate link עובד כראוי
"""
import os
from dotenv import load_dotenv

# טעינת המשתנים מ-.env
load_dotenv()

# הדפסת ה-associate tag
associate_tag = os.getenv('AMAZON_ASSOCIATE_TAG', 'not-set')
print(f"Amazon Associate Tag: {associate_tag}")
print(f"\nדוגמאות ל-URLs עם ה-associate tag שלך:\n")

# דוגמאות
examples = [
    "B0DT686HCZ",  # ProCase Screen Protector
    "B0D6W6G4Q4",  # SwarKing Display
]

for asin in examples:
    url = f"https://www.amazon.com/dp/{asin}?tag={associate_tag}"
    print(f"  • https://www.amazon.com/dp/{asin}?tag={associate_tag}")

print("\n[✓] כשמישהו ילחץ על אחד מהקישורים האלה וירכוש מוצר,")
print(f"    אתה תקבל עמלה כי הקישור כולל את ה-tag שלך: {associate_tag}")
print("\n[!] חשוב: וודא שאתה רשום כ-Amazon Associate עם ה-tag הזה")
print("    באתר: https://affiliate-program.amazon.com/")
