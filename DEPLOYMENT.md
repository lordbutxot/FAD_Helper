# Deployment Guide for F.A.D. Helper

## Free Hosting Options

### Option 1: Render.com (Recommended ⭐)

**Why Render?**
- Free PostgreSQL database included
- Automatic HTTPS/SSL
- Easy GitHub integration
- Auto-deploys on git push

**Steps:**
1. Push your code to GitHub
2. Go to [render.com](https://render.com) and sign up
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Render will detect `render.yaml` and set everything up automatically
6. Wait 5-10 minutes for initial deployment

**Important:**
- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Perfect for hobby/portfolio projects

---

### Option 2: PythonAnywhere

**Why PythonAnywhere?**
- Stays running 24/7 (no cold starts)
- Simple web interface
- Good for educational projects

**Steps:**
1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your code or clone from GitHub
3. Create a new web app (Flask/Python 3.13)
4. Configure WSGI file to point to your app
5. Install requirements: `pip install -r requirements.txt`
6. Initialize database: `python init_db.py`
7. Reload web app

**Limitations:**
- Manual deployment (no auto-deploy)
- Limited to one web app on free tier
- Must use SQLite (PostgreSQL not available on free tier)

---

### Option 3: Railway.app

**Why Railway?**
- Great developer experience
- PostgreSQL included
- Simple deployment

**Steps:**
1. Install Railway CLI: `npm install -g @railway/cli`
2. Run `railway login`
3. Run `railway init` in your project folder
4. Run `railway up`
5. Add PostgreSQL: `railway add --database postgresql`
6. Deploy: `railway up`

**Note:** Free tier gives $5/month credit (may run out with heavy usage)

---

### Option 4: Fly.io

**Why Fly.io?**
- Global edge deployment
- Fast performance
- Good free tier

**Requirements:**
- Need to create a Dockerfile
- More complex setup

**Steps:**
1. Install flyctl: `powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"`
2. Run `flyctl auth signup`
3. Run `flyctl launch` (will generate config)
4. Run `flyctl deploy`

---

## Pre-Deployment Checklist

### 1. Update requirements.txt
Add production dependencies:
```bash
pip install gunicorn psycopg2-binary python-dotenv
pip freeze > requirements.txt
```

### 2. Environment Variables
Set these on your hosting platform:
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `DATABASE_URL` - Provided by hosting platform
- `FLASK_ENV=production`

### 3. Database Migration (SQLite → PostgreSQL)
```python
# Export from SQLite
python -c "from app import app, db; from models import *; import json; with app.app_context(): users = User.query.all(); print(json.dumps([{'username': u.username} for u in users]))"

# Then manually migrate or use Flask-Migrate
```

### 4. Security Review
- [ ] `DEBUG = False` in production
- [ ] `SESSION_COOKIE_SECURE = True` (requires HTTPS)
- [ ] Secret key from environment variable
- [ ] Database backups configured
- [ ] .gitignore includes `.env`, `instance/`, `*.db`

### 5. Test Locally with Production Settings
```bash
$env:FLASK_ENV="production"
$env:SECRET_KEY="your-secret-key"
python app.py
```

---

## Post-Deployment

### Initialize Database
Most platforms have a console/shell feature:
```bash
python init_db.py
```

### Create Admin User
```bash
python create_admin.py
```

### Monitor
- Check application logs regularly
- Monitor database size (free tiers have limits)
- Watch for errors in hosting platform dashboard

---

## Cost Comparison

| Platform | Free Tier | Database | Cold Starts | Best For |
|----------|-----------|----------|-------------|----------|
| **Render** | 750hrs/mo | PostgreSQL (free) | Yes (30s) | Best overall |
| **PythonAnywhere** | 1 app | SQLite only | No | 24/7 availability |
| **Railway** | $5 credit/mo | PostgreSQL (free) | Minimal | Growing projects |
| **Fly.io** | 3 VMs | PostgreSQL add-on | Minimal | Global reach |

---

## Recommended: Render.com Setup

The `render.yaml` file is already configured. Just:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to render.com
   - New → Blueprint
   - Connect repository
   - Click "Apply"

3. **Initialize Database**
   - Once deployed, go to "Shell" in Render dashboard
   - Run: `python init_db.py`
   - Run: `python create_admin.py`

4. **Done!** Your app is live at `https://your-app-name.onrender.com`

---

## Troubleshooting

### "Application Error"
- Check logs in hosting platform
- Verify all environment variables are set
- Ensure database is connected

### "502 Bad Gateway"
- App is still starting (wait 30-60 seconds)
- Check if gunicorn is installed

### Database Connection Failed
- Verify DATABASE_URL is set correctly
- For Render: PostgreSQL URL might use `postgres://` (auto-fixed in config.py)
- Run `python init_db.py` to create tables

### CSS/Static Files Not Loading
- Check if static files are being served
- Verify `static/` folder is in git (not in .gitignore)
- May need to configure static file serving in hosting platform
