# בדיקת Affiliate ID - איך לדעת אם תקבל עמלה

## 📋 מה זה Affiliate ID?

זה המזהה שלך בתוכנית השותפים. כאשר מישהו לוחץ על הקישור שלך וקונה מוצר, החנות יודעת לזכות אותך בעמלה בזכות המזהה הזה.

## 🔍 איך לבדוק אם ה-URL מכיל את ה-ID שלך?

### Amazon Associate Tag
חפש בקישור את הפרמטר `tag=`:
```
https://www.amazon.com/dp/B08N5WRWNW?tag=YOUR-TAG-HERE
                                        ↑
                                   זה ה-ID שלך!
```

**דוגמה:**
```
https://www.amazon.com/dp/B08N5WRWNW?tag=goodsells02-20
```
כאן ה-tag שלך הוא: `goodsells02-20`

### AliExpress Tracking ID
חפש בקישור את הפרמטר `aff_trace_key=`:
```
https://www.aliexpress.com/item/123.html?aff_trace_key=YOUR-TRACKING-ID
                                         ↑
                                    זה ה-ID שלך!
```

## ✅ בדיקה אוטומטית בקונסול

כאשר תלחץ על כפתור "קנה עכשיו" על מוצר, תראה בקונסול (F12) הודעה כזו:

### ✅ אם ה-ID נמצא:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 AFFILIATE COMMISSION INFO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Product: Wireless Earbuds
🏪 Store: Amazon
💰 Price: $29.99
📊 Commission Rate: 3%
✅ Estimated Commission: $0.90

🔑 AFFILIATE ID CHECK:
✅ Affiliate ID Found: goodsells02-20
💵 You WILL receive commission when user buys!
🔗 URL contains your tracking ID

📋 Full URL:
https://www.amazon.com/dp/B08N5WRWNW?tag=goodsells02-20
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### ❌ אם ה-ID לא נמצא:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 AFFILIATE COMMISSION INFO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Product: Wireless Earbuds
🏪 Store: Amazon
💰 Price: $29.99
📊 Commission Rate: 3%
✅ Estimated Commission: $0.90

🔑 AFFILIATE ID CHECK:
❌ NO Affiliate ID Found!
⚠️ You will NOT receive commission!
🔧 Check your .env file and make sure:
   AMAZON_ASSOCIATE_TAG is set correctly

📋 Full URL:
https://www.amazon.com/dp/B08N5WRWNW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🔧 איך לתקן אם ה-ID לא נמצא?

1. **פתח את קובץ `.env`** בשורש הפרויקט
2. **הוסף/ערוך את השורות הבאות:**

```env
# Amazon Associate Tag
AMAZON_ASSOCIATE_TAG=your-associate-tag-20

# AliExpress Tracking ID
ALIEXPRESS_AFFILIATE_TRACKING=your-tracking-id
```

3. **החלף את הערכים** עם ה-IDs האמיתיים שלך:
   - `your-associate-tag-20` → ה-Associate Tag שלך מ-Amazon Associates
   - `your-tracking-id` → ה-Tracking ID שלך מ-AliExpress Affiliate Program

4. **הפעל מחדש את השרת**

## 📍 איפה למצוא את ה-IDs שלך?

### Amazon Associate Tag
1. היכנס ל-[Amazon Associates](https://affiliate-program.amazon.com/)
2. לחץ על "Account Settings"
3. תראה את ה-Tracking ID שלך (נקרא גם "Associate Tag")
4. בדרך כלל נראה כך: `yourname-20`

### AliExpress Tracking ID
1. היכנס ל-[AliExpress Affiliate Program](https://portals.aliexpress.com/)
2. לך ל-"Account Settings" או "Profile"
3. תמצא את ה-Tracking ID שלך

## 🎯 טיפים חשובים

- ✅ **תמיד בדוק בקונסול** לפני שאתה משתף קישורים
- ✅ **שמור את ה-IDs שלך במקום מאובטח** (קובץ .env)
- ✅ **אל תשתף את קובץ .env** ב-GitHub (כבר ב-.gitignore)
- ✅ **עדכן את Render** עם משתני הסביבה הנכונים
- ✅ **בדוק קישורים באופן קבוע** - לוודא שהם עובדים

## 🚀 הגדרת Render (Production)

כדי שהקישורים יעבדו ב-production:

1. היכנס ל-[Render Dashboard](https://dashboard.render.com)
2. בחר את השירות שלך
3. לך ל-"Environment"
4. הוסף את המשתנים:
   - `AMAZON_ASSOCIATE_TAG` = ה-tag שלך
   - `ALIEXPRESS_AFFILIATE_TRACKING` = ה-tracking ID שלך
5. שמור ולחץ "Deploy"

## ❓ שאלות נפוצות

**ש: האם אני צריך IDs שונים לכל מוצר?**
ת: לא, אותו ID משמש לכל המוצרים שלך.

**ש: מה קורה אם המשתמש לא קונה מיד?**
ת: ברוב המקרים יש cookie שתקף ל-24 שעות (Amazon) או 30 יום (AliExpress).

**ש: איך אדע כמה עמלה באמת קיבלתי?**
ת: היכנס לדשבורד השותפים שלך באתר החנות (Amazon Associates / AliExpress Affiliate).

**ש: האם העמלה בקונסול היא מדויקת?**
ת: זה אומדן. העמלה האמיתית תלויה בקטגוריית המוצר ובתנאים של תוכנית השותפים.
