# מדריך פריסה (Deployment) לאתר

האתר הזה הוא Flask application, ולכן **לא יכול לרוץ ישירות ב-GitHub Pages** (שתומך רק ב-static sites). צריך שירות אירוח שתומך ב-Python/Flask.

## אפשרויות פריסה 🚀

### 1. Render (מומלץ - חינמי!) ⭐

**Render** הוא שירות חינמי וקל לשימוש:

#### שלבים:

1. **צור חשבון ב-Render:**
   - גש ל-[render.com](https://render.com)
   - הירשם עם GitHub

2. **העלה את הפרויקט ל-GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

3. **צור Web Service ב-Render:**
   - לחץ על "New +" → "Web Service"
   - חבר את ה-repository שלך
   - הגדרות:
     - **Name**: `sells-website` (או כל שם)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py` או `gunicorn app:app`
     - **Plan**: Free

4. **הוסף Environment Variables:**
   - ב-Render, גש ל-Environment
   - הוסף את המשתנים מ-`.env`:
     - `AMAZON_ASSOCIATE_TAG`
     - `AMAZON_ACCESS_KEY` (אופציונלי)
     - `SECRET_KEY`

5. **האתר יעלה אוטומטית!**
   - Render ייתן לך URL כמו: `https://sells-website.onrender.com`

#### שיפור: שימוש ב-Gunicorn

הוסף ל-`requirements.txt`:
```
gunicorn==21.2.0
```

ושנה את Start Command ל:
```
gunicorn app:app --bind 0.0.0.0:$PORT
```

---

### 2. Railway 🚂

**Railway** - שירות נוסף, חינמי עם $5 credit:

1. **התחבר ל-Railway:**
   - גש ל-[railway.app](https://railway.app)
   - הירשם עם GitHub

2. **צור פרויקט חדש:**
   - לחץ על "New Project"
   - בחר "Deploy from GitHub repo"
   - בחר את ה-repository שלך

3. **Railway יזהה אוטומטית:**
   - Python application
   - יבנה ויריץ את האתר

4. **הוסף Environment Variables:**
   - ב-Variables, הוסף את המשתנים מ-`.env`

---

### 3. PythonAnywhere 🐍

**PythonAnyhouse** - חינמי לסטודנטים, אחרת $5/חודש:

1. **צור חשבון:**
   - גש ל-[pythonanywhere.com](https://www.pythonanywhere.com)
   - הירשם (חינמי לסטודנטים)

2. **העלה קבצים:**
   - העלה את כל הקבצים דרך Files
   - או חבר Git repository

3. **הגדר Web App:**
   - גש ל-Web
   - צור Web App חדש
   - בחר Flask
   - הגדר את ה-path ל-`app.py`

4. **הגדר Environment Variables:**
   - ב-Web → Static files
   - הוסף את המשתנים

---

### 4. Heroku ☁️

**Heroku** - שירות מקצועי (יש תשלום, אבל יש free tier מוגבל):

1. **התקן Heroku CLI:**
   ```bash
   # Windows
   choco install heroku-cli
   
   # Mac
   brew install heroku/brew/heroku
   ```

2. **צור Procfile:**
   ```
   web: gunicorn app:app
   ```

3. **הוסף runtime.txt:**
   ```
   python-3.11.0
   ```

4. **Deploy:**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

---

### 5. Vercel (עם Serverless Functions) ⚡

**Vercel** - מצוין ל-static + API routes:

1. **צור `vercel.json`:**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```

2. **Deploy:**
   ```bash
   npm i -g vercel
   vercel
   ```

---

## הגדרות חשובות ⚙️

### 1. הוסף `gunicorn` ל-requirements.txt

```txt
gunicorn==21.2.0
```

### 2. צור `Procfile` (ל-Heroku/Railway):

```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

### 3. עדכן את `app.py` לתמוך ב-PORT:

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### 4. הוסף `.gitignore`:

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
*.log
output_videos/
temp_files/
products.json
```

---

## המלצה 💡

**להתחלה מהירה:** השתמש ב-**Render** - חינמי, קל, ואוטומטי!

**לפרויקטים גדולים:** **Railway** או **Heroku** - יותר גמישים.

---

## פתרון בעיות 🔧

### השרת לא עולה
- ודא ש-`PORT` מוגדר נכון
- בדוק את ה-logs ב-Render/Railway

### שגיאות ב-build
- ודא ש-`requirements.txt` מעודכן
- בדוק שה-Python version תואם

### Environment Variables לא עובדים
- ודא שהוספת אותם ב-Render/Railway
- בדוק שאין שגיאות כתיב

---

**בהצלחה! 🚀**
