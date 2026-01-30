# GitHub Repository Setup Guide

## 🚀 Quick Deploy to GitHub

### 1. Initialize Git (if not already done)
```bash
git init
```

### 2. Create .gitignore (already created)
The `.gitignore` file is already configured to exclude:
- Virtual environments (.venv)
- Database files (*.db)
- Environment variables (.env)
- Python cache (__pycache__)
- Uploaded logos

### 3. Add All Files
```bash
git add .
```

### 4. Commit
```bash
git commit -m "Initial commit: FAD List Builder ready for deployment"
```

### 5. Create GitHub Repository
- Go to https://github.com/new
- Name your repository (e.g., `fad-list-builder`)
- **Don't** initialize with README, .gitignore, or license (we already have them)
- Click "Create repository"

### 6. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/fad-list-builder.git
git branch -M main
git push -u origin main
```

## 📦 Deploy to Render.com (Free Hosting)

### Option A: Blueprint Deploy (Easiest)
1. Push code to GitHub (steps above)
2. Go to https://render.com/dashboard
3. Click "New +" → "Blueprint"
4. Connect your GitHub account
5. Select your `fad-list-builder` repository
6. Render auto-detects `render.yaml` and creates:
   - Web service (Flask app)
   - PostgreSQL database
   - Environment variables
7. Click "Apply" and wait 5-10 minutes
8. Initialize database via Shell:
   ```bash
   python init_db.py
   python create_admin.py
   ```
9. Your app is live! 🎉

### Option B: Manual Deploy
1. Push code to GitHub
2. Go to Render dashboard
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure:
   - **Name**: fad-list-builder
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Add environment variables:
   - `SECRET_KEY` → Click "Generate" or use: `python -c "import secrets; print(secrets.token_hex(32))"`
   - `DATABASE_URL` → Link PostgreSQL database
   - `FLASK_ENV` → `production`
7. Create PostgreSQL database:
   - Click "New +" → "PostgreSQL"
   - Copy the Internal Database URL
   - Paste it as `DATABASE_URL` in web service
8. Deploy and initialize database

## 🛡️ Security Checklist

Before deploying, ensure:
- [x] `.gitignore` excludes `.env` and `*.db` files
- [x] `SECRET_KEY` is set from environment variable in production
- [x] `SESSION_COOKIE_SECURE = True` in production (HTTPS only)
- [x] Debug mode disabled in production
- [x] Database backups configured on hosting platform
- [x] No hardcoded passwords or secrets in code

## 📝 Post-Deployment

### Initialize Production Database
In Render Shell:
```bash
python init_db.py
```

### Create Admin Account
```bash
python create_admin.py
```
Follow prompts to create your admin user.

### Test Your App
1. Visit your Render URL (e.g., `https://fad-list-builder.onrender.com`)
2. Register a new account
3. Create a faction
4. Build a unit
5. Create an army list

## 🔄 Update Your App

When you make changes:
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

Render automatically redeploys on push! ⚡

## 📊 Monitoring

- **Logs**: View in Render dashboard
- **Database**: Monitor size in PostgreSQL dashboard
- **Metrics**: CPU, memory usage in Render dashboard
- **Errors**: Check logs if app crashes

## 🆘 Troubleshooting

### App won't start
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` has all dependencies

### Database errors
- Verify `DATABASE_URL` is set correctly
- Run `python init_db.py` in Shell
- Check database connection in logs

### Static files not loading
- Ensure `static/` folder is committed to git
- Check file paths are correct
- Verify Flask is serving static files correctly

## 🎯 Free Tier Limitations

**Render Free Tier:**
- Apps sleep after 15 minutes of inactivity
- 30-second cold start on first request
- 750 hours/month (plenty for hobby projects)
- Free PostgreSQL database (90 days, then $7/month)

**Tips:**
- Use a free uptime monitor (e.g., UptimeRobot) to ping your app every 30 min
- Or accept the cold starts for hobby use
- Upgrade to Starter plan ($7/month) for always-on service

## 🌟 Alternative Free Hosts

If Render doesn't work for you:
- **PythonAnywhere**: No cold starts, 24/7 availability
- **Railway**: $5/month credit (may run out with traffic)
- **Fly.io**: 3 VMs free, global deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides.

---

**Happy Deploying! 🚀**
