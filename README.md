# מערכת ליצירת סרטוני שיווק אוטומטיים 🎬

מערכת אוטומטית ליצירת סרטוני שיווק קצרים (8 שניות) למוצרים מחנויות שותפים כמו Amazon ו-AliExpress.

## תכונות ✨

- ✅ משיכת מוצרים אוטומטית מחנויות שותפים (Amazon, AliExpress)
- ✅ יצירת סרטוני שיווק אוטומטיים באורך 8 שניות
- ✅ פורמט אנכי (1080x1920) מותאם ל-TikTok/Instagram Reels
- ✅ תמיכה בעברית מלאה
- ✅ אנימציות וטקסטים דינמיים
- ✅ הצגת מחירים, הנחות ודירוגים

## התקנה 📦

### דרישות מערכת

- Python 3.8 או גבוה יותר
- FFmpeg (נדרש ל-MoviePy)

### התקנת FFmpeg

**Windows:**
1. הורד מ-[ffmpeg.org](https://ffmpeg.org/download.html)
2. הוסף ל-PATH או שמור ב-`C:\ffmpeg\bin`

**או באמצעות Chocolatey:**
```powershell
choco install ffmpeg
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# Mac
brew install ffmpeg
```

### התקנת תלויות Python

```bash
pip install -r requirements.txt
```

## הגדרה ⚙️

1. העתק את קובץ `.env.example` ל-`.env`:
```bash
copy .env.example .env  # Windows
# או
cp .env.example .env    # Linux/Mac
```

2. ערוך את קובץ `.env` והוסף את פרטי ה-API שלך:

### Amazon Associates API
- הירשם ל-[Amazon Associates](https://affiliate-program.amazon.com/)
- קבל `Access Key` ו-`Secret Key`
- הגדר `Associate Tag` שלך

### AliExpress Affiliate API
- הירשם ל-[AliExpress Affiliate Program](https://portals.aliexpress.com/)
- קבל `App Key` ו-`App Secret`

## שימוש 🚀

### יצירת סרטונים ממילות מפתח

```bash
# חיפוש מוצרים ב-Amazon
python main.py --keywords "טלפון חכם" --store amazon --count 3

# חיפוש מוצרים ב-AliExpress
python main.py --keywords "שעון חכם" --store aliexpress --count 5
```

### יצירת סרטון ממוצר בודד

```bash
# מ-URL של Amazon
python main.py --url "https://amazon.com/dp/B08N5WRWNW" --store amazon

# מ-URL של AliExpress
python main.py --url "https://aliexpress.com/item/1234567890.html" --store aliexpress
```

### פרמטרים

- `--keywords`: מילות מפתח לחיפוש מוצרים
- `--url`: URL של מוצר ספציפי
- `--store`: חנות שותפים (`amazon` או `aliexpress`)
- `--count`: מספר מוצרים ליצירה (ברירת מחדל: 5)

## מבנה הפרויקט 📁

```
sells/
├── main.py                 # סקריפט ראשי
├── product_fetcher.py      # מודול למשיכת מוצרים
├── video_generator.py      # מודול ליצירת סרטונים
├── requirements.txt        # תלויות Python
├── .env.example           # דוגמת תצורה
├── README.md              # קובץ זה
├── output_videos/         # תיקיית פלט (נוצרת אוטומטית)
└── temp_files/            # קבצים זמניים (נוצרת אוטומטית)
```

## מבנה הסרטון 🎥

כל סרטון (8 שניות) כולל:

1. **0-3 שניות**: תמונת מוצר עם אנימציית זום
2. **3-5 שניות**: כותרת המוצר
3. **5-7 שניות**: מחיר, הנחה ודירוג
4. **7-8 שניות**: קריאה לפעולה (CTA)

## פתרון בעיות 🔧

### שגיאת FFmpeg
אם אתה מקבל שגיאה הקשורה ל-FFmpeg:
- ודא ש-FFmpeg מותקן וזמין ב-PATH
- נסה להריץ: `ffmpeg -version` בטרמינל

### בעיות עם פונטים עבריים
המערכת מנסה להשתמש בפונטים עבריים מהמערכת. אם הטקסט לא מוצג נכון:
- ודא שיש פונט עברי מותקן (Arial, David, וכו')
- המערכת תשתמש בפונט ברירת מחדל אם לא נמצא פונט עברי

### בעיות עם API
אם אין לך פרטי API:
- המערכת תשתמש בנתוני דמה לבדיקה
- לקבלת נתונים אמיתיים, הגדר את פרטי ה-API ב-`.env`

## הערות חשובות ⚠️

1. **תוכנית שותפים**: ודא שיש לך חשבון פעיל בתוכנית השותפים של החנות
2. **תנאי שימוש**: הקפד לעמוד בתנאי השימוש של תוכניות השותפים
3. **תוכן**: ודא שהתוכן בסרטונים עומד בתנאי הפלטפורמה (TikTok, Instagram, וכו')

## פיתוח עתידי 🚀

- [ ] תמיכה בחנויות נוספות
- [ ] הוספת קול (TTS) לסרטונים
- [ ] תבניות סרטונים מותאמות אישית
- [ ] העלאה אוטומטית לרשתות חברתיות
- [ ] ניתוח ביצועים וסטטיסטיקות

## רישיון 📄

פרויקט זה הוא קוד פתוח וזמין תחת רישיון MIT.

## תמיכה 💬

לשאלות ובעיות, פתח issue ב-GitHub או צור קשר.

---

**נבנה עם ❤️ בישראל**
