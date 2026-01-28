# איך להוסיף מוצרים לאתר

יש לך מספר דרכים להוסיף מוצרים לאתר:

## דרך 1: דרך דף ניהול המוצרים (הקלה ביותר) 🎯

1. **פתח את האתר** - גש ל-`http://localhost:5000`
2. **לחץ על "ניהול מוצרים"** בתפריט העליון
3. **בחר סוג קישור**:
   - **קישור רגיל** - קישור מוצר רגיל מ-Amazon
   - **קישור שותפים (Affiliate Link)** - קישור עם פרמטר `tag=` או `linkId=`
4. **הדבק קישור מוצר** - העתק קישור מוצר מ-Amazon (לדוגמה: `https://www.amazon.com/dp/B08N5WRWNW`)
   - או קישור שותפים: `https://www.amazon.com/dp/B08N5WRWNW?tag=your-tag-20`
5. **לחץ על "הוסף מוצר"** - המוצר ייטען ויישמר אוטומטית

## דרך 2: דרך דף החיפוש 🔍

1. **פתח את דף הבית** או **דף המוצרים**
2. **חפש מוצרים** - הזן מילות מפתח (לדוגמה: "טלפון חכם")
3. **לחץ על "צור סרטון"** - זה יוצר סרטון וגם שומר את המוצר

## דרך 3: דרך API (לתכנות) 💻

### הוספת מוצר בודד (קישור רגיל):
```bash
curl -X POST http://localhost:5000/api/products/add \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/dp/B08N5WRWNW"}'
```

### הוספת מוצר דרך קישור שותפים (Affiliate Link):
```bash
curl -X POST http://localhost:5000/api/products/add \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/dp/B08N5WRWNW?tag=your-tag-20"}'
```

או:
```bash
curl -X POST http://localhost:5000/api/products/add \
  -H "Content-Type: application/json" \
  -d '{"affiliate_link": "https://www.amazon.com/dp/B08N5WRWNW?tag=your-tag-20"}'
```

### הוספת מוצר עם נתונים:
```bash
curl -X POST http://localhost:5000/api/products/add \
  -H "Content-Type: application/json" \
  -d '{
    "product": {
      "title": "מוצר מדהים",
      "price": "$29.99",
      "affiliate_url": "https://amazon.com/dp/..."
    }
  }'
```

## דרך 4: ייבוא מקובץ JSON 📁

1. **צור קובץ JSON** עם המוצרים שלך:
```json
{
  "products": [
    {
      "title": "מוצר 1",
      "price": "$29.99",
      "affiliate_url": "https://amazon.com/dp/B08N5WRWNW",
      "image_url": "https://...",
      "rating": 4.5,
      "reviews_count": 1234
    },
    {
      "title": "מוצר 2",
      "price": "$19.99",
      "affiliate_url": "https://amazon.com/dp/B08N5WRWNW",
      "image_url": "https://...",
      "rating": 4.8,
      "reviews_count": 567
    }
  ]
}
```

2. **פתח דף ניהול מוצרים** (`/manage`)
3. **לחץ על "ייבא מקובץ JSON"**
4. **בחר את הקובץ** - המוצרים ייובאו אוטומטית

## דרך 5: דרך קטגוריה של Amazon 📦

1. **מצא דף קטגוריה** ב-Amazon (לדוגמה: Best Sellers, Movers & Shakers)
2. **העתק את הקישור** לדף הקטגוריה
3. **פתח דף המוצרים** (`/products`)
4. **בחר "חיפוש לפי קטגוריה"**
5. **הדבק את הקישור** - כל המוצרים מהקטגוריה ייטענו

## דוגמאות לקישורים תקניים ✅

### קישור מוצר רגיל:
```
https://www.amazon.com/dp/B08N5WRWNW
```

### קישור שותפים (Affiliate Link) - מומלץ! 💰
```
https://www.amazon.com/dp/B08N5WRWNW?tag=your-tag-20
https://www.amazon.com/dp/B08N5WRWNW?tag=your-tag-20&linkCode=ogi&th=1
https://www.amazon.com/dp/B08N5WRWNW?tag=your-tag-20&linkId=XXXXX
```

**המערכת מזהה אוטומטית קישורי שותפים ומנקה אותם לפני חילוץ המידע!**

### קישור מוצר עם פרמטרים:
```
https://www.amazon.com/dp/B08N5WRWNW?ref=sr_1_1
```

### קישור מוצר קצר:
```
https://amzn.to/XXXXX
```

### קישור VDP (Video Detail Page):
```
https://www.amazon.com/vdp/...?product=B0D1G7XF9X
```

### קישור קטגוריה:
```
https://www.amazon.com/gp/bestsellers/electronics
https://www.amazon.com/gp/movers-and-shakers/electronics
```

## ניהול מוצרים שמורים 📋

### צפייה במוצרים שמורים:
- גש לדף **"ניהול מוצרים"** (`/manage`)
- כל המוצרים השמורים יוצגו ברשימה

### חיפוש במוצרים שמורים:
- השתמש בתיבת החיפוש בדף ניהול המוצרים
- חיפוש לפי שם או תיאור

### הסרת מוצר:
- לחץ על כפתור המחיקה (🗑️) ליד המוצר
- אישר את ההסרה

### ייצוא מוצרים:
- לחץ על **"ייצא לקובץ JSON"** בדף ניהול
- הקובץ יורד עם כל המוצרים השמורים

## טיפים 💡

1. **שמירה אוטומטית** - כל מוצר שמוסף נשמר אוטומטית בקובץ `products.json`
2. **עדכון אוטומטי** - אם מוסיפים מוצר שכבר קיים, הוא מתעדכן
3. **קישורי שותפים** - כל קישור נוצר אוטומטית עם ה-Associate Tag שלך
4. **סרטונים** - ניתן ליצור סרטון לכל מוצר שמור

## מיקום הקבצים 📂

- **מוצרים שמורים**: `products.json` (בתיקיית הפרויקט)
- **סרטונים שנוצרו**: `output_videos/`
- **קבצים זמניים**: `temp_files/`

---

**עזרה נוספת?** בדוק את `WEB_README.md` למידע נוסף על האתר.
